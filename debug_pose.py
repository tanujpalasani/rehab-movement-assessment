"""Quick diagnostic to check whether MediaPipe PoseLandmarker works."""
import os
import time

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

_MODEL_PATH = "pose_landmarker.task"

print(f"MediaPipe version: {mp.__version__}")
print(f"OpenCV version: {cv2.__version__}")

if not os.path.exists(_MODEL_PATH):
    print(f"[X] Model file NOT found: {_MODEL_PATH}")
    raise SystemExit(1)

print(f"[OK] Model file found: {_MODEL_PATH}")


def result_callback(result, output_image, timestamp_ms):
    if result.pose_landmarks:
        print(f"[OK] Landmarks detected at {timestamp_ms}ms")
    else:
        print(f". No pose seen at {timestamp_ms}ms")


base_options = mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=result_callback,
)

print("Testing camera and landmarker...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[X] Could not open camera")
    raise SystemExit(1)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    for _ in range(10):
        ret, frame = cap.read()
        if not ret:
            break

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        )
        landmarker.detect_async(mp_image, int(time.time() * 1000))
        time.sleep(0.1)

cap.release()
print("[OK] Diagnostic complete.")
