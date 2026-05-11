import cv2


_GROUP_COLORS = {
    "Elbow": {"title": (0, 220, 220), "border": (0, 180, 180)},
    "Knee": {"title": (220, 100, 255), "border": (180, 60, 200)},
    "Shoulder": {"title": (50, 200, 255), "border": (30, 160, 210)},
    "Wrist": {"title": (255, 150, 50), "border": (200, 100, 30)},
    "Hip": {"title": (150, 255, 50), "border": (100, 200, 30)},
}


def render_multi_exercise_overlay(frame, exercise_metrics_list):
    """Render a dynamic bilateral dashboard with clinical feedback."""
    fh, fw = frame.shape[:2]
    scale = fw / 640.0

    panel_w = int(180 * scale)
    panel_h = int(90 * scale)
    panel_margin = int(6 * scale)
    font = cv2.FONT_HERSHEY_SIMPLEX

    left_idx = 0
    right_idx = 0

    for ex in exercise_metrics_list:
        # Match group color by keyword in title
        group = "Elbow"
        for g in _GROUP_COLORS:
            if g in ex["title"]:
                group = g
                break
        colors = _GROUP_COLORS[group]

        if ex["side"] == "left":
            x_pos = int(10 * scale)
            y_idx = left_idx
            left_idx += 1
        else:
            x_pos = fw - panel_w - int(10 * scale)
            y_idx = right_idx
            right_idx += 1

        y_offset = int(10 * scale) + y_idx * (panel_h + panel_margin)
        if y_offset + panel_h > fh:
            continue

        # Background & border — highlight on warnings
        has_warning = ex.get("speed_warning") or ex.get("jerk_warning")
        bg_color = (10, 10, 50) if has_warning else (18, 18, 18)
        border_color = (0, 0, 255) if has_warning else colors["border"]

        cv2.rectangle(frame, (x_pos, y_offset),
                      (x_pos + panel_w, y_offset + panel_h),
                      bg_color, -1)
        cv2.rectangle(frame, (x_pos, y_offset),
                      (x_pos + panel_w, y_offset + panel_h),
                      border_color, 1)

        x_text = x_pos + int(10 * scale)
        y = y_offset + int(16 * scale)

        # Title
        cv2.putText(frame, ex["title"], (x_text, y),
                    font, 0.38 * scale, colors["title"], 1)

        # Angle + Reps
        y += int(18 * scale)
        status_color = (60, 200, 60) if ex["status"] == "Correct" else (50, 90, 230)
        cv2.putText(frame, f"{int(ex['angle'])} deg | Reps: {ex['reps']}",
                    (x_text, y), font, 0.32 * scale, status_color, 1)

        # Phase + Warnings
        y += int(16 * scale)
        if ex.get("speed_warning"):
            phase_text = "!! TOO FAST !!"
            phase_color = (0, 0, 255)
        elif ex.get("jerk_warning"):
            phase_text = "!! JERKY MOTION !!"
            phase_color = (0, 100, 255)
        else:
            phase_text = f"Phase: {ex['phase']}"
            phase_color = (200, 200, 200)

        cv2.putText(frame, phase_text, (x_text, y), font, 0.3 * scale, phase_color, 1)

        # ROM Feedback
        y += int(16 * scale)
        rom_text = ex["rom_feedback"]
        if "Good" in rom_text:
            rom_color = (60, 200, 60)
        elif "Fair" in rom_text:
            rom_color = (50, 170, 255)
        else:
            rom_color = (80, 80, 200)
        cv2.putText(frame, rom_text, (x_text, y), font, 0.3 * scale, rom_color, 1)

        # Joint Point Angle on body
        joint_point = ex.get("joint_point")
        if joint_point is not None:
            cv2.circle(frame, joint_point, max(2, int(4 * scale)), colors["title"], -1)
            cv2.putText(frame, f"{int(ex['angle'])}",
                        (joint_point[0] + 5, joint_point[1] - 5),
                        font, 0.4 * scale, colors["title"], 1)

    return frame