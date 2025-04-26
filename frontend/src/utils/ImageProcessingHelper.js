/**
 * ImageProcessingHelper - Provides utility functions for handling image processing
 * with YOLOv11 integration.
 */
class ImageProcessingHelper {
  /**
   * Draw bounding boxes on an image canvas for detected objects
   * 
   * @param {HTMLCanvasElement} canvas - Canvas element to draw on
   * @param {Object} detectionResults - Detection results from the API
   * @param {Object} options - Options for drawing
   */
  static drawDetections(canvas, detectionResults, options = {}) {
    const ctx = canvas.getContext('2d');
    
    // Default options
    const defaultOptions = {
      showLabels: true,
      showConfidence: true,
      personColor: 'rgba(0, 255, 0, 0.7)',      // Green for people
      equipmentColor: 'rgba(255, 0, 0, 0.7)',   // Red for safety equipment
      productColor: 'rgba(0, 0, 255, 0.7)',     // Blue for products
      defectColor: 'rgba(255, 165, 0, 0.7)',    // Orange for defects
      lineWidth: 2,
      fontSize: 14,
      fontFamily: 'Arial'
    };
    
    // Merge default options with provided options
    const opts = { ...defaultOptions, ...options };
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // No detections to display
    if (!detectionResults || !detectionResults.detections || detectionResults.detections.length === 0) {
      return;
    }
    
    // Draw each detection
    detectionResults.detections.forEach(detection => {
      const [x1, y1, x2, y2] = detection.bbox;
      const className = detection.class;
      const confidence = detection.confidence;
      
      // Determine color based on class
      let color;
      if (className === 'person') {
        color = opts.personColor;
      } else if (['helmet', 'hardhat', 'baret', 'goggles', 'gloves', 'vest', 'eldiven', 'gözlük'].includes(className)) {
        color = opts.equipmentColor;
      } else if (className.includes('defect')) {
        color = opts.defectColor;
      } else {
        color = opts.productColor;
      }
      
      // Draw rectangle
      ctx.strokeStyle = color;
      ctx.lineWidth = opts.lineWidth;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      
      // Draw label if enabled
      if (opts.showLabels) {
        let label = className;
        if (opts.showConfidence) {
          label += ` ${(confidence * 100).toFixed(0)}%`;
        }
        
        ctx.font = `${opts.fontSize}px ${opts.fontFamily}`;
        ctx.fillStyle = color;
        
        // Background for text
        const textWidth = ctx.measureText(label).width;
        ctx.fillRect(x1, y1 - opts.fontSize - 4, textWidth + 6, opts.fontSize + 6);
        
        // Text
        ctx.fillStyle = 'white';
        ctx.fillText(label, x1 + 3, y1 - 3);
      }
    });
    
    // Draw violations if present
    if (detectionResults.violations && detectionResults.violations.length > 0) {
      this.drawViolations(ctx, detectionResults.violations, opts);
    }
  }
  
  /**
   * Draw violation indicators
   * 
   * @param {CanvasRenderingContext2D} ctx - Canvas context
   * @param {Array} violations - Violation data
   * @param {Object} options - Drawing options
   */
  static drawViolations(ctx, violations, options) {
    violations.forEach(violation => {
      const [x1, y1, x2, y2] = violation.person_bbox;
      const violationType = violation.type;
      
      if (violationType === 'missing_equipment') {
        // Draw red X over person missing equipment
        ctx.strokeStyle = 'rgba(255, 0, 0, 0.8)';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x1, y2);
        ctx.lineTo(x2, y1);
        ctx.stroke();
        
        // Label what's missing
        const missingItem = violation.equipment_class || 'equipment';
        const label = `Missing ${missingItem}`;
        ctx.font = `${options.fontSize}px ${options.fontFamily}`;
        ctx.fillStyle = 'rgba(255, 0, 0, 0.9)';
        ctx.fillText(label, x1, y2 + 20);
      }
      else if (violationType === 'danger_zone') {
        // Highlight person in danger zone
        ctx.strokeStyle = 'rgba(255, 0, 0, 0.8)';
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        // Draw diagonal lines
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x1, y2);
        ctx.lineTo(x2, y1);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Label danger zone
        const zoneName = violation.zone_name || 'Danger Zone';
        const label = `In ${zoneName}`;
        ctx.font = `${options.fontSize}px ${options.fontFamily}`;
        ctx.fillStyle = 'rgba(255, 0, 0, 0.9)';
        ctx.fillText(label, x1, y2 + 20);
      }
    });
  }
  
  /**
   * Draw worker activity visualization
   */
  static drawWorkerActivities(canvas, activityResults, options = {}) {
    const ctx = canvas.getContext('2d');
    
    // Default options
    const defaultOptions = {
      workingColor: 'rgba(46, 204, 113, 0.7)',  // Green for working
      idleColor: 'rgba(231, 76, 60, 0.7)',      // Red for idle
      lineWidth: 2,
      fontSize: 14,
      fontFamily: 'Arial'
    };
    
    // Merge options
    const opts = { ...defaultOptions, ...options };
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // No activities to display
    if (!activityResults || !activityResults.activities || activityResults.activities.length === 0) {
      return;
    }
    
    // Draw workers
    if (activityResults.workers) {
      activityResults.workers.forEach(worker => {
        const [x1, y1, x2, y2] = worker.bbox;
        
        // Draw person bounding box
        ctx.strokeStyle = 'rgba(52, 152, 219, 0.7)';  // Blue
        ctx.lineWidth = opts.lineWidth;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      });
    }
    
    // Draw tools
    if (activityResults.tools) {
      activityResults.tools.forEach(tool => {
        const [x1, y1, x2, y2] = tool.bbox;
        const className = tool.class;
        
        // Draw tool bounding box
        ctx.strokeStyle = 'rgba(155, 89, 182, 0.7)';  // Purple
        ctx.lineWidth = opts.lineWidth;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        // Label
        ctx.font = `${opts.fontSize}px ${opts.fontFamily}`;
        ctx.fillStyle = 'rgba(155, 89, 182, 0.9)';
        ctx.fillText(className, x1, y1 - 5);
      });
    }
    
    // Draw activities
    activityResults.activities.forEach(activity => {
      const [x1, y1, x2, y2] = activity.person_bbox;
      const activityType = activity.activity_type;
      
      // Color based on activity
      const color = activityType === 'working' ? opts.workingColor : opts.idleColor;
      
      // Draw activity indicator (circle under the person)
      const centerX = (x1 + x2) / 2;
      const centerY = y2 + 15;
      const radius = 10;
      
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      
      // Draw activity label
      ctx.font = `${opts.fontSize}px ${opts.fontFamily}`;
      ctx.fillStyle = color;
      ctx.fillText(activityType.charAt(0).toUpperCase() + activityType.slice(1), centerX + 15, centerY + 5);
      
      // Draw nearby tools list if any
      if (activity.nearby_tools && activity.nearby_tools.length > 0) {
        const toolsLabel = `Tools: ${activity.nearby_tools.join(', ')}`;
        ctx.fillText(toolsLabel, x1, y2 + 35);
      }
    });
  }
  
  /**
   * Draw product count visualization
   */
  static drawProductCounts(canvas, countResults, options = {}) {
    const ctx = canvas.getContext('2d');
    
    // Default options
    const defaultOptions = {
      productColor: 'rgba(52, 152, 219, 0.7)',  // Blue for products
      defectColor: 'rgba(231, 76, 60, 0.7)',    // Red for defects
      lineWidth: 2,
      fontSize: 14,
      fontFamily: 'Arial'
    };
    
    // Merge options
    const opts = { ...defaultOptions, ...options };
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw products
    if (countResults.products) {
      countResults.products.forEach((product, index) => {
        const [x1, y1, x2, y2] = product.bbox;
        
        // Draw product bounding box
        ctx.strokeStyle = opts.productColor;
        ctx.lineWidth = opts.lineWidth;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        // Draw product number
        ctx.font = `bold ${opts.fontSize + 4}px ${opts.fontFamily}`;
        ctx.fillStyle = opts.productColor;
        ctx.fillText(`#${index + 1}`, x1 + 5, y1 + 20);
      });
    }
    
    // Draw defects
    if (countResults.defects) {
      countResults.defects.forEach(defect => {
        const [x1, y1, x2, y2] = defect.bbox;
        
        // Draw defect bounding box
        ctx.strokeStyle = opts.defectColor;
        ctx.lineWidth = opts.lineWidth;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        // Draw X mark
        ctx.beginPath();
        ctx.moveTo(x1 + 5, y1 + 5);
        ctx.lineTo(x2 - 5, y2 - 5);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x2 - 5, y1 + 5);
        ctx.lineTo(x1 + 5, y2 - 5);
        ctx.stroke();
        
        // Label
        ctx.font = `${opts.fontSize}px ${opts.fontFamily}`;
        ctx.fillStyle = opts.defectColor;
        ctx.fillText('Defect', x1, y1 - 5);
      });
    }
    
    // Draw count summary
    if (countResults.count !== undefined) {
      const countLabel = `Total: ${countResults.count}`;
      const defectLabel = `Defects: ${countResults.defect_count || 0}`;
      
      ctx.font = `bold ${opts.fontSize + 6}px ${opts.fontFamily}`;
      
      // Total count
      ctx.fillStyle = 'rgba(52, 152, 219, 0.9)';
      ctx.fillText(countLabel, 20, 30);
      
      // Defect count
      ctx.fillStyle = 'rgba(231, 76, 60, 0.9)';
      ctx.fillText(defectLabel, 20, 60);
    }
  }
  
  /**
   * Resize an image while maintaining aspect ratio
   */
  static resizeImage(imageFile, maxWidth, maxHeight) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        // Calculate new dimensions
        let width = img.width;
        let height = img.height;
        
        if (width > maxWidth) {
          height = (height * maxWidth) / width;
          width = maxWidth;
        }
        
        if (height > maxHeight) {
          width = (width * maxHeight) / height;
          height = maxHeight;
        }
        
        // Create canvas and resize
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        // Convert to Blob
        canvas.toBlob(blob => {
          resolve(blob);
        }, imageFile.type || 'image/jpeg');
      };
      
      img.onerror = reject;
      
      // Load image from File or Blob
      const url = URL.createObjectURL(imageFile);
      img.src = url;
    });
  }
  
  /**
   * Convert base64 string to Blob
   */
  static base64ToBlob(base64Data, contentType = 'image/jpeg') {
    // Extract base64 data
    const byteString = atob(base64Data.split(',')[1]);
    
    // Create ArrayBuffer and Uint8Array
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    
    return new Blob([ab], { type: contentType });
  }
  
  /**
   * Create a video thumbnail from a video file
   */
  static createVideoThumbnail(videoFile, seekTime = 0) {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.muted = true;
      video.playsInline = true;
      
      video.onloadedmetadata = () => {
        // Seek to the specified time
        video.currentTime = Math.min(seekTime, video.duration);
      };
      
      video.onseeked = () => {
        // Create canvas with video dimensions
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw current video frame
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to Blob
        canvas.toBlob(blob => {
          resolve(blob);
        }, 'image/jpeg', 0.8);
      };
      
      video.onerror = reject;
      
      // Load video
      video.src = URL.createObjectURL(videoFile);
    });
  }
}

export default ImageProcessingHelper;
