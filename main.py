import cv2
import logging
from ultralytics import YOLO
from SoundManager import SoundManager
from NerfController import NerfController

# Suppress ultralytics logging to reduce terminal output
logging.getLogger('ultralytics').setLevel(logging.WARNING)

# Initialize the sound manager and nerf controller
sound_manager = SoundManager()
nerf_controller = NerfController("COM4")

# Load the YOLOv8 model (nano version for speed; it will download automatically on first run)
model = YOLO('yolov8n.pt')

# Open the default webcam (0) or change to another index if needed
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to quit the detection.")


while True:
    # Read a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame from webcam.")
        break

    # Perform detection with YOLOv8
    results = model(frame, conf=0.5, classes=[0], verbose=False)  # conf=0.5 for confidence threshold, classes=[0] for person only

    # Check if any people were detected
    person_detected = any(len(result.boxes) > 0 for result in results)

    # Handle sound based on detection state
    sound_manager.handleSound(person_detected)

    # Draw rectangles around detected people
    biggest_box = None
    for result in results:
        for box in result.boxes:
            # Todo: sort by area if there are multiple people
            if biggest_box is None:
                biggest_box = box

    if biggest_box is not None:
        # Calculate the center of the biggest bounding box
        x1, y1, x2, y2 = biggest_box.xyxy[0].cpu().numpy()  # Get bounding box coordinates
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)


        # Draw visuals
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
        dX = center_x - frame.shape[1] // 2
        dY = center_y - frame.shape[0] // 2
        # Very simple PID loop (just the proportional part)
        # Tilting requires quicker response from experimentation
        nerf_controller.setScanDirection(dX)
        nerf_controller.moveBy(int(dX*0.03), int(dY*0.05))

        # Determine if we should rev and fire
        if abs(dX) < frame.shape[1] // 10 and abs(dY) < frame.shape[0] // 10:
            nerf_controller.firingUpdateLoop(True, True)
        elif abs(dX) < frame.shape[1] // 4 and abs(dY) < frame.shape[0] // 4:
            nerf_controller.firingUpdateLoop(True, False)
        else:
            nerf_controller.firingUpdateLoop(False, False)
    else:
        nerf_controller.scan()
        nerf_controller.firingUpdateLoop(False, False)

    # Display the frame with detections
    cv2.imshow('People Detection - YOLOv8', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()