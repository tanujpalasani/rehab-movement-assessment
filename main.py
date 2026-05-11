import cv2

from movement.analysis_module import ExerciseEvaluator, get_exercise_config
from movement.exercises import EXERCISE_CONFIGS
from pose.pose import PoseDetector
from ui.ui import render_multi_exercise_overlay


def run() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open camera. Please check camera availability and permissions.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = PoseDetector()

    # Create evaluators for all bilateral configs
    evaluators = {}
    for key, config in EXERCISE_CONFIGS.items():
        evaluators[key] = {"config": config, "evaluator": ExerciseEvaluator(config)}

    window_name = "Rehab System - Full Body"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    screen_w = cv2.getWindowImageRect(window_name)[2]
    screen_h = cv2.getWindowImageRect(window_name)[3]
    if screen_w <= 0: screen_w, screen_h = 1280, 720

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.resize(frame, (screen_w, screen_h))
            frame, coords = detector.get_pose(frame)

            metrics_to_render = []
            
            if coords:
                for key, entry in evaluators.items():
                    config = entry["config"]
                    evaluator = entry["evaluator"]
                    
                    metrics = evaluator.evaluate(coords)
                    if metrics:
                        # DYNAMIC VISIBILITY: 
                        # Only show panel if movement is detected (ROM > threshold)
                        # OR if it's the "active" phase of a rep.
                        if metrics.rom > config.display_threshold or metrics.reps > 0:
                            metrics_to_render.append({
                                "title": config.title,
                                "side": config.side,
                                "angle": metrics.angle,
                                "rom": metrics.rom,
                                "reps": metrics.reps,
                                "status": metrics.status,
                                "rom_feedback": metrics.rom_feedback,
                                "hint": metrics.hint,
                                "joint_point": tuple(map(int, metrics.joint_point)) if metrics.joint_point else None,
                                "phase": metrics.phase,
                                "speed_warning": metrics.speed_warning,
                                "jerk_warning": metrics.jerk_warning,
                            })

            frame = render_multi_exercise_overlay(frame, metrics_to_render)
            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27: break
            elif key == ord('f'):
                curr = cv2.getWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, 1 - curr)

    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
