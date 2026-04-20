import os
import sys
import threading
import time
from typing import Optional

import cv2
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from movement.evaluator import ExerciseEvaluator
from movement.exercises import EXERCISE_CONFIGS, get_exercise_config
from pose.pose import PoseDetector
from ui import render_exercise_overlay

PROCESS_EVERY_N_FRAMES = 3
WORKER_TARGET_FPS = 20


class CameraWorker:
    def __init__(self, exercise_key: str) -> None:
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

        self.cap: Optional[cv2.VideoCapture] = None
        self.detector: Optional[PoseDetector] = None
        self.evaluator = ExerciseEvaluator(get_exercise_config(exercise_key))
        self.exercise_key = exercise_key

        self.running = False
        self.pose_available = False
        self.status = "Idle"
        self.read_failures = 0
        self.frame_index = 0
        self.latest_frame_rgb = None
        self.latest_metrics = {
            "exercise_title": self.evaluator.config.title,
            "angle": 0.0,
            "rom": 0.0,
            "reps": 0,
            "status": "No person detected",
            "rom_feedback": "Incomplete movement",
            "hint": "Step into frame and keep full body visible.",
            "joint_point": None,
        }

    def update_exercise(self, exercise_key: str) -> None:
        with self.lock:
            self.exercise_key = exercise_key
            self.evaluator.update_config(get_exercise_config(exercise_key))
            self.latest_metrics = {
                "exercise_title": self.evaluator.config.title,
                "angle": 0.0,
                "rom": 0.0,
                "reps": 0,
                "status": "Exercise updated",
                "rom_feedback": "Incomplete movement",
                "hint": self.evaluator.config.description,
                "joint_point": None,
            }

    def start(self) -> bool:
        if self.running:
            return True

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.status = "Could not open camera. Check device permissions."
            return False

        # Keep latency low and frame delivery stable for larger displays.
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        self.cap = cap
        self.detector = PoseDetector()
        self.pose_available = self.detector.available
        self.read_failures = 0
        self.frame_index = 0
        self.latest_frame_rgb = None
        self.latest_metrics = {
            "exercise_title": self.evaluator.config.title,
            "angle": 0.0,
            "rom": 0.0,
            "reps": 0,
            "status": "Ready",
            "rom_feedback": "Incomplete movement",
            "hint": self.evaluator.config.description,
            "joint_point": None,
        }
        self.status = "Running"

        self.stop_event.clear()
        self.running = True
        self.thread = threading.Thread(target=self._loop, name="camera-worker", daemon=True)
        self.thread.start()
        return True

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=1.5)

        if self.detector is not None:
            self.detector.close()
        if self.cap is not None:
            self.cap.release()

        self.thread = None
        self.detector = None
        self.cap = None
        self.running = False
        self.status = "Stopped"

    def _loop(self) -> None:
        frame_interval = 1.0 / WORKER_TARGET_FPS

        while not self.stop_event.is_set():
            loop_start = time.perf_counter()

            if self.cap is None:
                self.status = "Camera not initialized"
                time.sleep(0.05)
                continue

            ret, frame = self.cap.read()
            if not ret:
                self.read_failures += 1
                if self.read_failures >= 60:
                    self.status = "Camera read failed repeatedly"
                    self.stop_event.set()
                time.sleep(0.01)
                continue

            self.read_failures = 0
            self.frame_index += 1

            metrics = self.latest_metrics
            if self.detector is not None and self.frame_index % PROCESS_EVERY_N_FRAMES == 0:
                frame, coords = self.detector.get_pose(frame)
                evaluation = self.evaluator.evaluate(coords)

                if evaluation is not None:
                    metrics = {
                        "exercise_title": self.evaluator.config.title,
                        "angle": evaluation.angle,
                        "rom": evaluation.rom,
                        "reps": evaluation.reps,
                        "status": evaluation.status,
                        "rom_feedback": evaluation.rom_feedback,
                        "hint": evaluation.hint,
                        "joint_point": evaluation.joint_point,
                    }
                else:
                    metrics = {
                        "exercise_title": self.evaluator.config.title,
                        "angle": 0.0,
                        "rom": 0.0,
                        "reps": self.evaluator.reps,
                        "status": "No person detected",
                        "rom_feedback": "Incomplete movement",
                        "hint": "Keep your full right side visible to the camera.",
                        "joint_point": None,
                    }

                self.latest_metrics = metrics

            frame = render_exercise_overlay(
                frame,
                metrics["exercise_title"],
                metrics["angle"],
                metrics["rom"],
                metrics["reps"],
                metrics["status"],
                metrics["rom_feedback"],
                metrics["hint"],
                metrics["joint_point"],
            )
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            with self.lock:
                self.latest_frame_rgb = frame_rgb

            elapsed = time.perf_counter() - loop_start
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)

        self.running = False

    def get_latest_frame(self):
        with self.lock:
            if self.latest_frame_rgb is None:
                return None
            return self.latest_frame_rgb.copy()

    def get_metrics(self):
        with self.lock:
            return dict(self.latest_metrics)


def _ensure_runtime_state() -> None:
    if "camera_running" not in st.session_state:
        st.session_state.camera_running = False
    if "camera_worker" not in st.session_state:
        st.session_state.camera_worker = None
    if "camera_placeholder" not in st.session_state:
        st.session_state.camera_placeholder = None
    if "selected_exercise" not in st.session_state:
        st.session_state.selected_exercise = "elbow_flexion"
    if "metrics_placeholder" not in st.session_state:
        st.session_state.metrics_placeholder = None


def _start_runtime() -> bool:
    worker = st.session_state.camera_worker
    if worker is not None and worker.running:
        return True

    worker = CameraWorker(st.session_state.selected_exercise)
    ok = worker.start()
    if not ok:
        st.error(worker.status)
        return False

    st.session_state.camera_worker = worker
    st.session_state.camera_running = True
    return True


def _stop_runtime() -> None:
    worker = st.session_state.camera_worker
    if worker is not None:
        worker.stop()

    st.session_state.camera_worker = None
    st.session_state.camera_placeholder = None
    st.session_state.metrics_placeholder = None
    st.session_state.camera_running = False


def run_camera_stream() -> None:
    worker = st.session_state.camera_worker
    if worker is None or not worker.running:
        st.warning("Camera runtime is not initialized.")
        st.session_state.camera_running = False
        return

    if not worker.pose_available:
        st.warning(
            "Pose backend is unavailable in this MediaPipe build. "
            "Install a solutions-capable MediaPipe/Python combination to enable detection."
        )

    frame = worker.get_latest_frame()
    if frame is None:
        st.info("Initializing camera feed...")
        return

    metrics = worker.get_metrics()

    if st.session_state.camera_placeholder is None:
        st.session_state.camera_placeholder = st.empty()
    if st.session_state.metrics_placeholder is None:
        st.session_state.metrics_placeholder = st.empty()

    st.session_state.camera_placeholder.image(
        frame,
        channels="RGB",
        width="stretch",
    )

    status_is_correct = metrics["status"] == "Correct"
    status_color = "#1f9d55" if status_is_correct else "#d94848"

    st.session_state.metrics_placeholder.markdown(
        f"""
        <div style='padding: 14px; border: 1px solid #2b2f36; border-radius: 10px; margin-top: 10px;'>
            <div style='display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 8px;'>
                <div><strong>Exercise</strong><br>{metrics['exercise_title']}</div>
                <div><strong>Angle</strong><br>{metrics['angle']:.1f}&deg;</div>
                <div><strong>ROM</strong><br>{metrics['rom']:.1f}&deg;</div>
                <div><strong>Reps</strong><br>{metrics['reps']}</div>
            </div>
            <div style='margin-top: 10px;'><strong>Status</strong>:
                <span style='color: {status_color}; font-weight: 700;'>{metrics['status']}</span>
            </div>
            <div style='margin-top: 6px;'><strong>ROM Feedback</strong>: {metrics['rom_feedback']}</div>
            <div style='margin-top: 6px;'><strong>Hint</strong>: {metrics['hint']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.fragment(run_every="140ms")
def camera_fragment() -> None:
    if st.session_state.camera_running:
        run_camera_stream()


def _render_home_page() -> None:
    st.subheader("Project Overview")
    st.write(
        "This application analyzes rehabilitation exercises using live pose estimation "
        "and real-time joint-angle feedback."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("Exercises: Elbow Flexion, Squat, Shoulder Raise")
    with c2:
        st.info("Live Metrics: Angle, ROM, Repetition Count")
    with c3:
        st.info("Posture Guidance: Correct/Incorrect with hints")


def _render_instructions_page() -> None:
    st.subheader("Instructions")
    st.markdown(
        """
1. Stand 1.5 to 2 meters away from the camera.
2. Keep your full right side visible (shoulder, elbow, hip, knee, ankle).
3. Select an exercise from the sidebar.
4. Press Start Detection and move smoothly.
5. Use Stop Detection before changing camera setup.
        """
    )

    st.warning("If detection drops: improve lighting, keep the camera steady, and reduce background clutter.")


def _render_start_exercise_page() -> None:
    options = list(EXERCISE_CONFIGS.keys())
    selected = st.sidebar.selectbox(
        "Select Exercise",
        options=options,
        format_func=lambda key: EXERCISE_CONFIGS[key].title,
        index=options.index(st.session_state.selected_exercise),
    )

    if selected != st.session_state.selected_exercise:
        st.session_state.selected_exercise = selected
        worker = st.session_state.camera_worker
        if worker is not None and worker.running:
            worker.update_exercise(selected)

    st.write(EXERCISE_CONFIGS[selected].description)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Detection", type="primary", width="stretch"):
            _start_runtime()
    with col2:
        if st.button("Stop Detection", width="stretch"):
            _stop_runtime()

    camera_fragment()

    if not st.session_state.camera_running:
        st.info("Camera is off. Start detection to begin the exercise.")


def main() -> None:
    st.set_page_config(page_title="Rehab Vision Coach", layout="wide")
    st.title("Rehabilitation Movement Range Assessment")
    st.caption("Rehabilitation demo using computer vision and real-time posture feedback.")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Start Exercise", "Instructions"])

    _ensure_runtime_state()

    if page == "Home":
        _render_home_page()
    elif page == "Instructions":
        _render_instructions_page()
    else:
        _render_start_exercise_page()


if __name__ == "__main__":
    main()
