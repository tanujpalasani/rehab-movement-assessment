"""Quick diagnostic to check if modern MediaPipe PoseLandmarker works."""
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import os
import time

# Resolve model path
_MODEL_PATH = "pose_landmarker.task"

print(f"MediaPipe version: {mp.__version__}")
print(f"OpenCV version: {cv2.__version__}")

if not os.path.exists(_MODEL_PATH):
    print(f"✗ Model file NOT found: {_MODEL_PATH}")
    exit(1)

print(f"✓ Model file found: {_MODEL_PATH}")

# Callback for results
def result_callback(result, output_image, timestamp_ms):
    if result.pose_landmarks:
        print(f"✓ Landmarks detected at {timestamp_ms}ms")
    else:
        print(f". No pose seen at {timestamp_ms}ms")

# Setup Options
base_options = mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=result_callback
)

# Test detection
print("Testing camera and landmarker...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("✗ Could not open camera")
    exit(1)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    for i in range(10):
        ret, frame = cap.read()
        if not ret: break
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        landmarker.detect_async(mp_image, int(time.time() * 1000))
        time.sleep(0.1)

cap.release()
print("✓ Diagnostic complete.")
