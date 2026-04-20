import cv2


def render_exercise_overlay(frame, exercise_title, angle, rom, reps, status, rom_feedback, hint, joint_point=None):
    status_color = (60, 200, 60) if status == "Correct" else (50, 90, 230)

    cv2.rectangle(frame, (10, 10), (560, 220), (18, 18, 18), -1)
    cv2.rectangle(frame, (10, 10), (560, 220), (65, 65, 65), 1)

    cv2.putText(frame, exercise_title,
                (24, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (245, 245, 245), 2)

    cv2.putText(frame, f"Joint Angle: {int(angle)} deg",
                (24, 78),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (120, 230, 120), 2)

    cv2.putText(frame, f"ROM: {int(rom)} deg   Reps: {reps}",
                (24, 112),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (120, 170, 255), 2)

    rom_color = (60, 200, 60) if rom_feedback == "Good Range of Motion" else (50, 170, 255)
    if rom_feedback == "Incomplete movement":
        rom_color = (0, 120, 255)

    cv2.putText(frame, f"ROM Feedback: {rom_feedback}",
                (24, 146),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62, rom_color, 2)

    cv2.putText(frame, f"Status: {status}",
                (24, 178),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, status_color, 2)

    cv2.putText(frame, f"Hint: {hint}",
                (24, 208),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (230, 230, 230), 1)

    if joint_point is not None:
        cv2.circle(frame, joint_point, 6, (0, 220, 220), -1)
        cv2.putText(frame, f"{int(angle)} deg",
                    (joint_point[0] + 10, joint_point[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 240, 240), 2)

    return frame


def render_ui(frame, coords, angle, rom, feedback):
    # Backward-compatible wrapper used by older app code paths.
    return render_exercise_overlay(
        frame,
        exercise_title="Rehab Session",
        angle=angle,
        rom=rom,
        reps=0,
        status="Correct" if feedback and "No" not in feedback else "Incorrect",
        rom_feedback=feedback,
        hint=feedback,
        joint_point=coords.get("elbow") if isinstance(coords, dict) else None,
    )