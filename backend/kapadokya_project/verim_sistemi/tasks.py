import os
import cv2
import numpy as np
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from ultralytics import YOLO

from kapadokya_project.api.models import ProcessedImage
from .models import (
    Worker, WorkArea, WorkerActivity, ProductivityData,
    Product, ProductionCount
)

# Load YOLO models
def get_worker_activity_model():
    """Load the YOLOv11 model for worker activity detection"""
    model_path = os.path.join(settings.YOLO_MODEL_PATH, 'worker_activity_model.pt')
    return YOLO(model_path)

def get_product_detection_model():
    """Load the YOLOv11 model for product detection"""
    model_path = os.path.join(settings.YOLO_MODEL_PATH, 'product_detection_model.pt')
    return YOLO(model_path)

@shared_task
def process_productivity_image_task(processed_image_id, work_area_id):
    """Process an image with YOLOv11 to detect worker activities"""
    try:
        processed_image = ProcessedImage.objects.get(id=processed_image_id)
        work_area = WorkArea.objects.get(id=work_area_id)
        
        # Get the original image path
        image_path = processed_image.original_image.path
        image = cv2.imread(image_path)
        
        if image is None:
            # Failed to read the image
            processed_image.detection_results = {"error": "Görüntü okunamadı"}
            processed_image.save()
            return False
        
        # Load YOLOv11 model
        model = get_worker_activity_model()
        
        # Run detection on the image
        results = model(image)
        
        # Process the results
        detection_results = {
            "workers": [],
            "activities": [],
            "tools": []
        }
        
        # Extract detected persons and their activities
        person_detections = []
        tool_detections = []
        
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
                
                # Track person detections
                if class_name == "person":
                    person_detections.append(detection)
                    detection_results["workers"].append(detection)
                
                # Track tool detections
                elif "tool" in class_name or class_name in ["hammer", "drill", "saw", "wrench"]:
                    tool_detections.append(detection)
                    detection_results["tools"].append(detection)
        
        # Try to identify workers and their activities
        for person in person_detections:
            person_x1, person_y1, person_x2, person_y2 = person["bbox"]
            person_center = ((person_x1 + person_x2) // 2, (person_y1 + person_y2) // 2)
            
            # Identify if worker is idle, working, etc. based on posture and context
            # This is a simplified example - in a real system, you would need more sophisticated activity recognition
            nearby_tools = []
            for tool in tool_detections:
                tool_x1, tool_y1, tool_x2, tool_y2 = tool["bbox"]
                # Check if tool is close to person
                if (abs((tool_x1 + tool_x2) // 2 - person_center[0]) < 200 and 
                    abs((tool_y1 + tool_y2) // 2 - person_center[1]) < 200):
                    nearby_tools.append(tool["class"])
            
            # Determine activity based on tools and posture
            if nearby_tools:
                activity_type = "working"
            else:
                activity_type = "idle"  # Simplified - should be determined by posture analysis
            
            # Add activity to results
            activity = {
                "person_bbox": person["bbox"],
                "activity_type": activity_type,
                "nearby_tools": nearby_tools,
                "confidence": person["confidence"]
            }
            detection_results["activities"].append(activity)
            
            # Create worker activity record in database
            # In a real system, you would use facial recognition or other methods to identify specific workers
            WorkerActivity.objects.create(
                processed_image=processed_image,
                # worker=None,  # Would be set if worker can be identified
                work_area=work_area,
                activity_type=activity_type,
                detected_tools=nearby_tools,
                confidence=person["confidence"],
                duration=0  # Would be calculated by comparing with previous frames
            )
        
        # Draw detections on the image
        annotated_image = draw_productivity_annotations(image, detection_results)
        
        # Save the processed image
        processed_image_path = os.path.join(
            settings.MEDIA_ROOT, 
            f"processed/productivity_{processed_image_id}.jpg"
        )
        cv2.imwrite(processed_image_path, annotated_image)
        
        # Update the ProcessedImage record
        processed_image.processed_image = f"processed/productivity_{processed_image_id}.jpg"
        processed_image.detection_results = detection_results
        processed_image.save()
        
        return True
    
    except Exception as e:
        # Log the error
        print(f"Error processing productivity image {processed_image_id}: {str(e)}")
        
        # Update the record with error info
        try:
            processed_image = ProcessedImage.objects.get(id=processed_image_id)
            processed_image.detection_results = {"error": str(e)}
            processed_image.save()
        except:
            pass
        
        return False

def draw_productivity_annotations(image, detection_results):
    """Draw worker activities annotations on the image"""
    img = image.copy()
    
    # Draw workers (persons)
    for worker in detection_results.get("workers", []):
        x1, y1, x2, y2 = worker["bbox"]
        conf = worker["confidence"]
        
        # Draw bounding box for workers
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw label
        label = f"Worker {conf:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw tools
    for tool in detection_results.get("tools", []):
        x1, y1, x2, y2 = tool["bbox"]
        cls = tool["class"]
        conf = tool["confidence"]
        
        # Draw bounding box for tools
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        # Draw label
        label = f"{cls} {conf:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # Draw activities
    for activity in detection_results.get("activities", []):
        x1, y1, x2, y2 = activity["person_bbox"]
        activity_type = activity["activity_type"]
        
        # Color based on activity type
        if activity_type == "working":
            color = (0, 255, 0)  # Green for working
        elif activity_type == "idle":
            color = (0, 0, 255)  # Red for idle
        else:
            color = (255, 255, 0)  # Yellow for other activities
        
        # Draw activity label
        cv2.putText(
            img, 
            activity_type.capitalize(), 
            (x1, y2 + 20), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.6, 
            color, 
            2
        )
        
        # Draw tools label if any
        tools = ", ".join(activity.get("nearby_tools", []))
        if tools:
            cv2.putText(
                img, 
                f"Tools: {tools}", 
                (x1, y2 + 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                color, 
                1
            )
    
    return img

@shared_task
def process_product_count_task(processed_image_id, product_id):
    """Process an image with YOLOv11 to count products"""
    try:
        processed_image = ProcessedImage.objects.get(id=processed_image_id)
        product = Product.objects.get(id=product_id)
        
        # Get the original image path
        image_path = processed_image.original_image.path
        image = cv2.imread(image_path)
        
        if image is None:
            # Failed to read the image
            processed_image.detection_results = {"error": "Görüntü okunamadı"}
            processed_image.save()
            return False
        
        # Load YOLOv11 model
        model = get_product_detection_model()
        
        # Run detection on the image
        results = model(image)
        
        # Process the results
        detection_results = {
            "products": [],
            "defects": [],
            "count": 0,
            "defect_count": 0
        }
        
        # Extract detected products
        product_detections = []
        defect_detections = []
        
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
                
                # Check if this is our target product
                if class_name == product.detection_class:
                    product_detections.append(detection)
                    detection_results["products"].append(detection)
                    detection_results["count"] += 1
                
                # Check if this is a defect
                elif class_name == f"{product.detection_class}_defect":
                    defect_detections.append(detection)
                    detection_results["defects"].append(detection)
                    detection_results["defect_count"] += 1
        
        # Draw detections on the image
        annotated_image = draw_product_count_annotations(image, detection_results, product.name)
        
        # Save the processed image
        processed_image_path = os.path.join(
            settings.MEDIA_ROOT, 
            f"processed/product_count_{processed_image_id}.jpg"
        )
        cv2.imwrite(processed_image_path, annotated_image)
        
        # Update the ProcessedImage record
        processed_image.processed_image = f"processed/product_count_{processed_image_id}.jpg"
        processed_image.detection_results = detection_results
        processed_image.save()
        
        # Update or create ProductionCount record for today
        today = timezone.now().date()
        production_count, created = ProductionCount.objects.update_or_create(
            product=product,
            camera=processed_image.camera,
            date=today,
            defaults={
                'count': detection_results["count"],
                'defect_count': detection_results["defect_count"],
                'details': {
                    'image_id': processed_image_id,
                    'timestamp': timezone.now().isoformat()
                }
            }
        )
        
        return True
    
    except Exception as e:
        # Log the error
        print(f"Error processing product count image {processed_image_id}: {str(e)}")
        
        # Update the record with error info
        try:
            processed_image = ProcessedImage.objects.get(id=processed_image_id)
            processed_image.detection_results = {"error": str(e)}
            processed_image.save()
        except:
            pass
        
        return False

def draw_product_count_annotations(image, detection_results, product_name):
    """Draw product count annotations on the image"""
    img = image.copy()
    
    # Draw detected products
    for product in detection_results.get("products", []):
        x1, y1, x2, y2 = product["bbox"]
        conf = product["confidence"]
        
        # Draw bounding box for products
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw label
        label = f"{product_name} {conf:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw defects
    for defect in detection_results.get("defects", []):
        x1, y1, x2, y2 = defect["bbox"]
        conf = defect["confidence"]
        
        # Draw bounding box for defects
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        # Draw label
        label = f"Defect {conf:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Draw count information
    count = detection_results.get("count", 0)
    defect_count = detection_results.get("defect_count", 0)
    
    cv2.putText(
        img, 
        f"Total: {count}", 
        (20, 30), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        1, 
        (0, 0, 0), 
        2
    )
    
    cv2.putText(
        img, 
        f"Defects: {defect_count}", 
        (20, 70), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        1, 
        (0, 0, 255), 
        2
    )
    
    return img

@shared_task
def generate_daily_productivity_report():
    """Generate daily productivity reports for all workers"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Get all active workers
    workers = Worker.objects.filter(is_active=True)
    
    for worker in workers:
        # Get all work areas this worker worked in yesterday
        work_areas = set(
            WorkerActivity.objects.filter(
                worker=worker,
                timestamp__date=yesterday
            ).values_list('work_area_id', flat=True)
        )
        
        for work_area_id in work_areas:
            try:
                work_area = WorkArea.objects.get(id=work_area_id)
                
                # Get all activities for this worker in this work area yesterday
                activities = WorkerActivity.objects.filter(
                    worker=worker,
                    work_area=work_area,
                    timestamp__date=yesterday
                )
                
                # Calculate time spent in each activity type
                working_time = sum([a.duration for a in activities.filter(activity_type='working')])
                idle_time = sum([a.duration for a in activities.filter(activity_type='idle')])
                absent_time = sum([a.duration for a in activities.filter(activity_type='absent')])
                break_time = sum([a.duration for a in activities.filter(activity_type='break')])
                
                # Calculate productivity score (simplified example)
                total_time = working_time + idle_time + absent_time + break_time
                if total_time > 0:
                    productivity_score = (working_time / total_time) * 100
                else:
                    productivity_score = 0
                
                # Create or update productivity data record
                ProductivityData.objects.update_or_create(
                    worker=worker,
                    work_area=work_area,
                    date=yesterday,
                    defaults={
                        'working_time': working_time,
                        'idle_time': idle_time,
                        'absent_time': absent_time,
                        'break_time': break_time,
                        'productivity_score': productivity_score,
                        'details': {
                            'activity_count': activities.count(),
                            'tools_used': list(set([
                                tool for act in activities 
                                for tool in act.detected_tools or []
                            ]))
                        }
                    }
                )
                
                print(f"Generated productivity report for {worker.name} in {work_area.name}")
                
            except WorkArea.DoesNotExist:
                continue
            except Exception as e:
                print(f"Error generating productivity report for {worker.name}: {str(e)}")
    
    return True
