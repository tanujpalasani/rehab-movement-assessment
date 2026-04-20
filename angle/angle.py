import math


def calculate_joint_angle(point_a, point_b, point_c):
    """Return the angle ABC in degrees for 2D points A, B, C."""
    angle = math.degrees(
        math.atan2(point_c[1] - point_b[1], point_c[0] - point_b[0]) -
        math.atan2(point_a[1] - point_b[1], point_a[0] - point_b[0])
    )

    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle

    return float(angle)


def calculate_angle(coords):
    """Backward-compatible helper for the right elbow angle."""
    required = ("shoulder", "elbow", "wrist")
    for key in required:
        if key not in coords:
            raise ValueError(f"Missing coordinate: {key}")

    shoulder = coords["shoulder"]
    elbow = coords["elbow"]
    wrist = coords["wrist"]

    # Convert to vectors
    a = shoulder
    b = elbow
    c = wrist

    return calculate_joint_angle(a, b, c)
