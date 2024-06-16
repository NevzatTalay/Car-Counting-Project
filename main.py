import torch
import cv2
import numpy as np

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # Choose from 'yolov5s', 'yolov5m', 'yolov5l', 'yolov5x'

# Read the video file
video_path = 'Cars Moving On Road Stock Footage - Free Download.mp4'  # Path to your video file
cap = cv2.VideoCapture(video_path)

# Counter and line coordinates
counter = 0
line_position = 200  # Position of the line in y-axis
tracking_offset = 30  # Tolerance for comparing previous position of the object
line_crossing_offset = 10  # Tolerance for detecting line crossing

# Object tracking information
tracked_objects = {}
object_id = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Video ended or cannot be read.")
        break

    # Apply YOLOv5 model to the frame
    results = model(frame)

    # Mark detected objects
    current_objects = []
    for pred in results.pred[0]:
        x1, y1, x2, y2, conf, cls = pred
        label = model.names[int(cls)]
        if label == 'car':  # Detect cars
            # Calculate the center coordinates of the car
            center_y = int((y1 + y2) / 2)
            center_x = int((x1 + x2) / 2)

            # Add current detected objects to the list
            current_objects.append((center_x, center_y))

            # Determine the car ID
            same_object_detected = False
            for obj_id, obj_coords in tracked_objects.items():
                previous_x, previous_y = obj_coords[-1]
                if abs(previous_x - center_x) < tracking_offset and abs(previous_y - center_y) < tracking_offset:
                    tracked_objects[obj_id].append((center_x, center_y))
                    same_object_detected = True
                    break

            if not same_object_detected:
                tracked_objects[object_id] = [(center_x, center_y)]
                object_id += 1

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(frame, f'{label} {conf:.2f}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Mark the center point

    # Count cars crossing the line
    for obj_id, obj_coords in tracked_objects.items():
        for i in range(1, len(obj_coords)):
            previous_x, previous_y = obj_coords[i-1]
            current_x, current_y = obj_coords[i]
            if previous_y < line_position <= current_y:
                counter += 1
                tracked_objects[obj_id] = [(current_x, current_y)]  # Reset list after counting
                break

    # Draw the line
    cv2.line(frame, (0, line_position), (frame.shape[1], line_position), (0, 255, 0), 2)
    cv2.putText(frame, f'Counter: {counter}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the result
    cv2.imshow('YOLOv5 Car Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()