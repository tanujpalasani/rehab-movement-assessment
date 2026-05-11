from __future__ import annotations

import os
from typing import Dict, Tuple

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# Resolve model path relative to project root
_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pose_landmarker.task",
)

# Landmark indices matching the PoseLandmarker output (same as legacy PoseLandmark enum)
_JOINT_MAP = {
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_index": 19,
    "right_index": 20,
}


class PoseDetector:
    def __init__(self):
        self.available = os.path.isfile(_MODEL_PATH)
        self.unavailable_reason = "" if self.available else f"Model file not found: {_MODEL_PATH}"
        self._latest_result = None
        self._timestamp_ms = 0

        if self.available:
            base_options = mp_python.BaseOptions(
                model_asset_path=_MODEL_PATH,
            )
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.LIVE_STREAM,
                num_poses=1,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                output_segmentation_masks=False,
                result_callback=self._result_callback,
            )
            self.landmarker = vision.PoseLandmarker.create_from_options(options)
        else:
            self.landmarker = None

    def _result_callback(self, result, output_image, timestamp_ms):
        """Callback for LIVE_STREAM mode."""
        self._latest_result = result

    def close(self) -> None:
        if self.landmarker is not None:
            try:
                self.landmarker.close()
            except Exception:
                pass

    def get_pose(self, frame) -> Tuple[cv2.typing.MatLike, Dict[str, Tuple[float, float]]]:
        if self.landmarker is None:
            return frame, {}

        h, w, _ = frame.shape

        # Convert BGR to RGB and create MediaPipe Image
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Send frame asynchronously
        self._timestamp_ms += 33  # ~30 fps
        self.landmarker.detect_async(mp_image, self._timestamp_ms)

        coords = {}

        if self._latest_result and self._latest_result.pose_landmarks:
            pose_landmarks = self._latest_result.pose_landmarks[0]  # First person

            for name, idx in _JOINT_MAP.items():
                lm = pose_landmarks[idx]
                if lm.visibility < 0.3:
                    continue
                coords[name] = (lm.x * w, lm.y * h)

            # Backward-compatible aliases for existing angle utility and tests.
            if "right_shoulder" in coords:
                coords["shoulder"] = coords["right_shoulder"]
            if "right_elbow" in coords:
                coords["elbow"] = coords["right_elbow"]
            if "right_wrist" in coords:
                coords["wrist"] = coords["right_wrist"]

            # Draw skeleton on frame
            self._draw_landmarks(frame, pose_landmarks, h, w)

        return frame, coords

    def _draw_landmarks(self, frame, landmarks, h, w):
        """Draw pose landmarks and connections on the frame."""
        # Define connections (pairs of landmark indices)
        connections = [
            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Arms
            (11, 23), (12, 24), (23, 24),  # Torso
            (23, 25), (25, 27), (24, 26), (26, 28),  # Legs
        ]

        # Draw connections
        for start_idx, end_idx in connections:
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            if start.visibility < 0.3 or end.visibility < 0.3:
                continue
            pt1 = (int(start.x * w), int(start.y * h))
            pt2 = (int(end.x * w), int(end.y * h))
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

        # Draw landmark points
        for idx in _JOINT_MAP.values():
            lm = landmarks[idx]
            if lm.visibility < 0.3:
                continue
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)