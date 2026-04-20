import cv2

from angle.angle import calculate_angle
from feedback.feedback import generate_feedback
from movement.analysis import MovementAnalyzer
from pose.pose import PoseDetector
from ui.ui import render_ui


def run() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open camera. Please check camera availability and permissions.")
        return

    detector = PoseDetector()
    analyzer = MovementAnalyzer()

    if not detector.available:
        print(
            "Warning: Pose backend unavailable in this MediaPipe build. "
            "Running camera feed without pose landmarks."
        )

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame, coords = detector.get_pose(frame)
            if coords:
                angle = calculate_angle(coords)
                rom, _, _ = analyzer.update(angle)
                feedback = generate_feedback(rom)
            else:
                angle, rom, feedback = 0.0, 0.0, "No detection"

            frame = render_ui(frame, coords, angle, rom, feedback)
            cv2.imshow("Rehab System", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
