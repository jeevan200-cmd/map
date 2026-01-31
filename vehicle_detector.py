"""
Vehicle Detection Module using YOLOv8
This module provides functionality to detect and classify vehicles from images and videos
"""

import cv2
import numpy as np
from pathlib import Path

class YOLOVehicleDetector:
    """
    Vehicle detection class using YOLOv8
    Detects and classifies: bikes, cars, buses, trucks
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the detector
        
        Args:
            model_path: Path to YOLO model weights (optional)
        """
        self.model_path = model_path
        self.vehicle_classes = {
            'bicycle': 'bike',
            'motorcycle': 'bike',
            'car': 'car',
            'bus': 'bus',
            'truck': 'truck'
        }
        
        # Try to load YOLOv8 model
        try:
            from ultralytics import YOLO
            if model_path and Path(model_path).exists():
                self.model = YOLO(model_path)
            else:
                # Use pretrained YOLOv8n model
                self.model = YOLO('yolov8n.pt')
            self.use_yolo = True
            print("✓ YOLOv8 model loaded successfully")
        except Exception as e:
            print(f"⚠ Could not load YOLO model: {e}")
            print("  Using demo mode with simulated detections")
            self.model = None
            self.use_yolo = False
    
    def detect_from_image(self, image_path, confidence_threshold=0.5):
        """
        Detect vehicles in an image
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            List of detections with type, confidence, and bounding box
        """
        if self.use_yolo and self.model:
            return self._detect_with_yolo(image_path, confidence_threshold)
        else:
            return self._generate_demo_detections()
    
    def _detect_with_yolo(self, image_path, confidence_threshold):
        """Detect vehicles using actual YOLO model"""
        results = self.model(image_path, conf=confidence_threshold)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = float(box.conf[0])
                
                # Check if it's a vehicle class we're interested in
                if class_name.lower() in self.vehicle_classes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    detections.append({
                        'type': self.vehicle_classes[class_name.lower()],
                        'confidence': confidence,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'class_name': class_name
                    })
        
        return detections
    
    def _generate_demo_detections(self):
        """Generate demo detections for testing without YOLO model"""
        num_detections = np.random.randint(5, 15)
        detections = []
        
        vehicle_types = ['bike', 'car', 'bus', 'truck']
        weights = [0.15, 0.55, 0.15, 0.15]  # More cars, fewer bikes/buses/trucks
        
        for _ in range(num_detections):
            v_type = np.random.choice(vehicle_types, p=weights)
            
            detections.append({
                'type': v_type,
                'confidence': np.random.uniform(0.7, 0.95),
                'bbox': [
                    np.random.randint(0, 800),
                    np.random.randint(0, 600),
                    np.random.randint(0, 800),
                    np.random.randint(0, 600)
                ]
            })
        
        return detections
    
    def detect_from_video(self, video_path, frame_skip=5):
        """
        Detect vehicles in a video
        
        Args:
            video_path: Path to video file
            frame_skip: Process every Nth frame
            
        Returns:
            Dictionary with total counts and frame-by-frame results
        """
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        vehicle_counts = {'bike': 0, 'car': 0, 'bus': 0, 'truck': 0}
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every Nth frame
            if frame_count % frame_skip == 0:
                # Save frame temporarily
                temp_frame = f'temp_frame_{frame_count}.jpg'
                cv2.imwrite(temp_frame, frame)
                
                # Detect vehicles
                detections = self.detect_from_image(temp_frame)
                
                # Count vehicles
                for det in detections:
                    vehicle_counts[det['type']] += 1
                
                # Clean up
                Path(temp_frame).unlink(missing_ok=True)
            
            frame_count += 1
        
        cap.release()
        
        return {
            'total_frames': frame_count,
            'processed_frames': frame_count // frame_skip,
            'vehicle_counts': vehicle_counts,
            'total_vehicles': sum(vehicle_counts.values())
        }
    
    def draw_detections(self, image_path, output_path, detections):
        """
        Draw bounding boxes on image
        
        Args:
            image_path: Input image path
            output_path: Output image path
            detections: List of detections
        """
        img = cv2.imread(image_path)
        
        colors = {
            'bike': (255, 0, 255),    # Magenta
            'car': (255, 0, 0),       # Blue
            'bus': (0, 0, 255),       # Red
            'truck': (0, 165, 255)    # Orange
        }
        
        for det in detections:
            bbox = det['bbox']
            v_type = det['type']
            confidence = det['confidence']
            
            color = colors.get(v_type, (0, 255, 0))
            
            # Draw bounding box
            cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw label
            label = f"{v_type}: {confidence:.2f}"
            cv2.putText(img, label, (bbox[0], bbox[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        cv2.imwrite(output_path, img)
        return output_path


# Traffic line counter class
class TrafficLineCounter:
    """
    Count vehicles crossing a virtual line
    """
    
    def __init__(self, line_position, direction='horizontal'):
        """
        Args:
            line_position: Y coordinate for horizontal line, X for vertical
            direction: 'horizontal' or 'vertical'
        """
        self.line_position = line_position
        self.direction = direction
        self.tracked_objects = {}
        self.count = 0
    
    def update(self, detections, frame_number):
        """
        Update counts based on new detections
        
        Args:
            detections: List of vehicle detections
            frame_number: Current frame number
        """
        for det in detections:
            bbox = det['bbox']
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            
            # Check if vehicle crossed the line
            if self.direction == 'horizontal':
                if center_y > self.line_position:
                    self.count += 1
            else:  # vertical
                if center_x > self.line_position:
                    self.count += 1
        
        return self.count
