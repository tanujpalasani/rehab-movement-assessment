from __future__ import annotations

from typing import Dict, Tuple

import cv2
import mediapipe as mp

mp_pose = None
mp_drawing = None
_POSE_IMPORT_ERROR = ""

try:
    # MediaPipe on newer Python builds may only expose Tasks and omit solutions.
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
except (AttributeError, ImportError) as exc:
    _POSE_IMPORT_ERROR = str(exc)


class PoseDetector:
    def __init__(self):
        self.available = mp_pose is not None
        self.unavailable_reason = _POSE_IMPORT_ERROR
        self.pose = (
            mp_pose.Pose(
                static_image_mode=False,
                model_complexity=0,
                smooth_landmarks=True,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            if self.available
            else None
        )

    def _recreate_pose(self) -> None:
        if not self.available:
            self.pose = None
            return

        try:
            if self.pose is not None:
                self.pose.close()
        except ValueError:
            # Ignore graph-state errors while recovering from a failed run.
            pass

        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def close(self) -> None:
        if self.pose is not None:
            try:
                self.pose.close()
            except ValueError:
                # Streamlit reruns can race with graph shutdown; ignore safe-close errors.
                pass

    def get_pose(self, frame) -> Tuple[cv2.typing.MatLike, Dict[str, Tuple[int, int]]]:
        if self.pose is None:
            return frame, {}

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        try:
            result = self.pose.process(rgb)
        except ValueError:
            # Recover from intermittent MediaPipe graph timestamp mismatch errors.
            self._recreate_pose()
            return frame, {}

        coords = {}

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark

            h, w, _ = frame.shape

            joint_map = {
                "left_shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER,
                "right_shoulder": mp_pose.PoseLandmark.RIGHT_SHOULDER,
                "left_elbow": mp_pose.PoseLandmark.LEFT_ELBOW,
                "right_elbow": mp_pose.PoseLandmark.RIGHT_ELBOW,
                "left_wrist": mp_pose.PoseLandmark.LEFT_WRIST,
                "right_wrist": mp_pose.PoseLandmark.RIGHT_WRIST,
                "left_hip": mp_pose.PoseLandmark.LEFT_HIP,
                "right_hip": mp_pose.PoseLandmark.RIGHT_HIP,
                "left_knee": mp_pose.PoseLandmark.LEFT_KNEE,
                "right_knee": mp_pose.PoseLandmark.RIGHT_KNEE,
                "left_ankle": mp_pose.PoseLandmark.LEFT_ANKLE,
                "right_ankle": mp_pose.PoseLandmark.RIGHT_ANKLE,
            }

            for name, landmark_id in joint_map.items():
                landmark = landmarks[landmark_id]
                if landmark.visibility < 0.5:
                    continue
                coords[name] = (
                    int(landmark.x * w),
                    int(landmark.y * h),
                )

            # Backward-compatible aliases for existing angle utility and tests.
            if "right_shoulder" in coords:
                coords["shoulder"] = coords["right_shoulder"]
            if "right_elbow" in coords:
                coords["elbow"] = coords["right_elbow"]
            if "right_wrist" in coords:
                coords["wrist"] = coords["right_wrist"]

            # Draw skeleton when drawing tools are available.
            if mp_drawing is not None:
                mp_drawing.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

        return frame, coords