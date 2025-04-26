import os
import cv2
import numpy as np
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from ultralytics import YOLO
from kapadokya_project.api.models import ProcessedImage, Zone
from .models import SafetyEquipment, SafetyViolation, SafetyReport

# Load YOLO models
def get_isg_model():
    """Load the YOLOv11 model for safety equipment detection"""
    model_path = os.path.join(settings.YOLO_MODEL_PATH, 'isg_model.pt')
    return YOLO(model_path)

@shared_task
def process_image_task(processed_image_id):
    """Process an image with YOLOv11 to detect safety violations"""
    try:
        processed_image = ProcessedImage.objects.get(id=processed_image_id)
        
        # Get the original image path
        image_path = processed_image.original_image.path
        image = cv2.imread(image_path)
        
        if image is None:
            # Failed to read the image
            processed_image.detection_results = {"error": "Görüntü okunamadı"}
            processed_image.save()
            return False
        
        # Load YOLOv11 model
        model = get_isg_model()
        
        # Run detection on the image
        results = model(image)
        
        # Process the results
        detection_results = {
            "detections": [],
            "violations": []
        }
        
        # Get safety equipment requirements
        required_equipment = SafetyEquipment.objects.filter(required=True)
        required_classes = {eq.detection_class: eq.id for eq in required_equipment}
        
        # Get zones for this camera
        danger_zones = Zone.objects.filter(
            camera=processed_image.camera, 
            is_danger_zone=True
        )
        
        # Extract detected objects
        detected_classes = {}
        person_detections = []
        
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].astype(int)
                conf = box.conf[0]
                cls = int(box.cls[0])
                class_name = result.names[cls]
                
                detection = {
                    "class": class_name,
                    "confidence": float(conf),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                }
                detection_results["detections"].append(detection)
                
                # Track detected classes for equipment verification
                if class_name in required_classes:
                    if class_name not in detected_classes:
                        detected_classes[class_name] = []
                    detected_classes[class_name].append(detection)
                
                # Track person detections for zone violations
                if class_name == "person":
                    person_detections.append(detection)
        
        # Check for safety equipment violations
        for person in person_detections:
            person_x1, person_y1, person_x2, person_y2 = person["bbox"]
            missing_equipment = []
            
            # For each required equipment, check if it's detected near this person
            for eq_class, eq_id in required_classes.items():
                found = False
                
                if eq_class in detected_classes:
                    for eq_detection in detected_classes[eq_class]:
                        eq_x1, eq_y1, eq_x2, eq_y2 = eq_detection["bbox"]
                        
                        # Check if equipment is near the person (simple overlap check)
                        if (eq_x1 < person_x2 and eq_x2 > person_x1 and 
                            eq_y1 < person_y2 and eq_y2 > person_y1):
                            found = True
                            break
                
                if not found:
                    missing_equipment.append({
                        "equipment_id": eq_id,
                        "equipment_class": eq_class
                    })
            
            # If missing equipment, record violations
            for missing in missing_equipment:
                violation = {
                    "type": "missing_equipment",
                    "equipment_id": missing["equipment_id"],
                    "person_bbox": person["bbox"],
                    "confidence": person["confidence"]
                }
                detection_results["violations"].append(violation)
                
                # Create violation record in database
                SafetyViolation.objects.create(
                    processed_image=processed_image,
                    violation_type="missing_equipment",
                    equipment_id=missing["equipment_id"],
                    confidence=person["confidence"]
                )
        
        # Check for danger zone violations
        for person in person_detections:
            person_x1, person_y1, person_x2, person_y2 = person["bbox"]
            person_center = ((person_x1 + person_x2) // 2, (person_y1 + person_y2) // 2)
            
            for zone in danger_zones:
                # Convert zone coordinates from JSON to numpy array
                zone_coords = np.array(zone.coordinates, dtype=np.int32)
                
                # Check if person is in the danger zone
                if cv2.pointPolygonTest(zone_coords, person_center, False) >= 0:
                    violation = {
                        "type": "danger_zone",
                        "zone_id": zone.id,
                        "zone_name": zone.name,
                        "person_bbox": person["bbox"],
                        "confidence": person["confidence"]
                    }
                    detection_results["violations"].append(violation)
                    
                    # Create violation record in database
                    SafetyViolation.objects.create(
                        processed_image=processed_image,
                        violation_type="danger_zone",
                        zone=zone,
                        confidence=person["confidence"]
                    )
        
        # Draw detections and violations on the image
        annotated_image = draw_detections(image, detection_results)
        
        # Save the processed image
        processed_image_path = os.path.join(
            settings.MEDIA_ROOT, 
            f"processed/processed_{processed_image_id}.jpg"
        )
        cv2.imwrite(processed_image_path, annotated_image)
        
        # Update the ProcessedImage record
        processed_image.processed_image = f"processed/processed_{processed_image_id}.jpg"
        processed_image.detection_results = detection_results
        processed_image.save()
        
        return True
    
    except Exception as e:
        # Log the error
        print(f"Error processing image {processed_image_id}: {str(e)}")
        
        # Update the record with error info
        try:
            processed_image = ProcessedImage.objects.get(id=processed_image_id)
            processed_image.detection_results = {"error": str(e)}
            processed_image.save()
        except:
            pass
        
        return False

def draw_detections(image, detection_results):
    """Draw bounding boxes and violation indicators on the image"""
    img = image.copy()
    
    # Draw all detections
    for detection in detection_results["detections"]:
        x1, y1, x2, y2 = detection["bbox"]
        cls = detection["class"]
        conf = detection["confidence"]
        
        # Different colors for different classes
        if cls == "person":
            color = (0, 255, 0)  # Green for people
        elif cls in ["helmet", "hardhat", "baret"]:
            color = (255, 0, 0)  # Red for helmet/hardhat
        elif cls in ["vest", "safety_vest", "yelek"]:
            color = (0, 0, 255)  # Blue for vests
        elif cls in ["gloves", "eldiven"]:
            color = (255, 255, 0)  # Yellow for gloves
        elif cls in ["goggles", "safety_glasses", "gözlük"]:
            color = (255, 0, 255)  # Purple for goggles
        else:
            color = (180, 180, 180)  # Gray for other objects
        
        # Draw bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"{cls} {conf:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Highlight violations
    for violation in detection_results["violations"]:
        if violation["type"] == "missing_equipment":
            # Draw a red X over the person missing equipment
            x1, y1, x2, y2 = violation["person_bbox"]
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.line(img, (x1, y2), (x2, y1), (0, 0, 255), 3)
            
            # Label the missing equipment
            equipment_class = violation.get("equipment_class", "equipment")
            label = f"Missing {equipment_class}"
            cv2.putText(img, label, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        elif violation["type"] == "danger_zone":
            # Highlight person in danger zone with a red box
            x1, y1, x2, y2 = violation["person_bbox"]
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
            # Label the danger zone violation
            zone_name = violation.get("zone_name", "Danger Zone")
            label = f"In {zone_name}"
            cv2.putText(img, label, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    return img

@shared_task
def generate_daily_safety_report(date_str=None):
    """Generate daily safety report"""
    try:
        if date_str:
            report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            report_date = timezone.now().date() - timedelta(days=1)
        
        # Get all violations for the day
        start_date = datetime.combine(report_date, datetime.min.time())
        end_date = datetime.combine(report_date, datetime.max.time())
        
        violations = SafetyViolation.objects.filter(
            timestamp__range=(start_date, end_date)
        )
        
        # Count violations by type
        total_violations = violations.count()
        resolved_violations = violations.filter(resolved=True).count()
        missing_equipment_count = violations.filter(violation_type='missing_equipment').count()
        danger_zone_count = violations.filter(violation_type='danger_zone').count()
        unauthorized_entry_count = violations.filter(violation_type='unauthorized_entry').count()
        
        # Count violations by hour
        hourly_data = {}
        for hour in range(24):
            hour_start = datetime.combine(report_date, datetime.min.time()) + timedelta(hours=hour)
            hour_end = hour_start + timedelta(hours=1)
            
            hour_violations = violations.filter(
                timestamp__range=(hour_start, hour_end)
            ).count()
            
            hourly_data[str(hour)] = hour_violations
        
        # Prepare report data
        report_data = {
            "hourly_violations": hourly_data,
            "violation_types": {
                "missing_equipment": missing_equipment_count,
                "danger_zone": danger_zone_count,
                "unauthorized_entry": unauthorized_entry_count
            },
            "resolution_rate": (resolved_violations / total_violations) if total_violations > 0 else 0
        }
        
        # Create or update the report
        report, created = SafetyReport.objects.update_or_create(
            report_date=report_date,
            defaults={
                'total_violations': total_violations,
                'resolved_violations': resolved_violations,
                'missing_equipment_count': missing_equipment_count,
                'danger_zone_count': danger_zone_count,
                'unauthorized_entry_count': unauthorized_entry_count,
                'report_data': report_data
            }
        )
        
        return True
    
    except Exception as e:
        print(f"Error generating safety report: {str(e)}")
        return False
