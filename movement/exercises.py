from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ExerciseConfig:
    key: str
    title: str
    side: str  # "left" or "right"
    description: str
    triplet: Tuple[str, str, str]
    target_min: float
    target_max: float
    low_hint: str
    high_hint: str
    rep_low: float
    rep_high: float
    # Clinical Refinements
    max_speed: float = 750.0  # degrees per SECOND threshold for "Too Fast"
    jerk_threshold: float = 300.0  # velocity variance threshold for jerkiness
    display_threshold: float = 15.0  # ROM needed to show panel
    # Rep direction: "low_first" means you go below rep_low then above rep_high.
    # "high_first" means you go above rep_high first then below rep_low.
    rep_direction: str = "low_first"
    # Phase labels (customizable per exercise)
    phase_a_label: str = "Flexing"
    phase_b_label: str = "Extending"


EXERCISE_CONFIGS: Dict[str, ExerciseConfig] = {
    # ELBOWS — bend first (angle decreases), then straighten (angle increases)
    "right_elbow_flexion": ExerciseConfig(
        key="right_elbow_flexion", title="R Elbow Flexion", side="right",
        description="Bend and extend your right elbow.",
        triplet=("right_shoulder", "right_elbow", "right_wrist"),
        target_min=45.0, target_max=165.0,
        low_hint="Open elbow more.", high_hint="Bend elbow further.",
        rep_low=65.0, rep_high=145.0,
        rep_direction="low_first",
        phase_a_label="Bending", phase_b_label="Straightening"
    ),
    "left_elbow_flexion": ExerciseConfig(
        key="left_elbow_flexion", title="L Elbow Flexion", side="left",
        description="Bend and extend your left elbow.",
        triplet=("left_shoulder", "left_elbow", "left_wrist"),
        target_min=45.0, target_max=165.0,
        low_hint="Open elbow more.", high_hint="Bend elbow further.",
        rep_low=65.0, rep_high=145.0,
        rep_direction="low_first",
        phase_a_label="Bending", phase_b_label="Straightening"
    ),
    # SHOULDERS — raise arm (angle decreases toward 35), lower (increases toward 120)
    "right_shoulder_abduction": ExerciseConfig(
        key="right_shoulder_abduction", title="R Shoulder Abduction", side="right",
        description="Raise your right arm sideways. 120 safety cap.",
        triplet=("right_elbow", "right_shoulder", "right_hip"),
        target_min=35.0, target_max=120.0,
        low_hint="Lower arm slightly.", high_hint="Raise arm higher.",
        rep_low=50.0, rep_high=105.0,
        rep_direction="low_first",
        phase_a_label="Raising", phase_b_label="Lowering"
    ),
    "left_shoulder_abduction": ExerciseConfig(
        key="left_shoulder_abduction", title="L Shoulder Abduction", side="left",
        description="Raise your left arm sideways. 120 safety cap.",
        triplet=("left_elbow", "left_shoulder", "left_hip"),
        target_min=35.0, target_max=120.0,
        low_hint="Lower arm slightly.", high_hint="Raise arm higher.",
        rep_low=50.0, rep_high=105.0,
        rep_direction="low_first",
        phase_a_label="Raising", phase_b_label="Lowering"
    ),
    # KNEES — bend (angle decreases), stand (angle increases)
    "right_squat": ExerciseConfig(
        key="right_squat", title="R Knee Flexion", side="right",
        description="Lower and rise smoothly.",
        triplet=("right_hip", "right_knee", "right_ankle"),
        target_min=70.0, target_max=170.0,
        low_hint="Keep control.", high_hint="Lower hips more.",
        rep_low=95.0, rep_high=155.0,
        rep_direction="low_first",
        phase_a_label="Squatting", phase_b_label="Rising"
    ),
    "left_squat": ExerciseConfig(
        key="left_squat", title="L Knee Flexion", side="left",
        description="Lower and rise smoothly.",
        triplet=("left_hip", "left_knee", "left_ankle"),
        target_min=70.0, target_max=170.0,
        low_hint="Keep control.", high_hint="Lower hips more.",
        rep_low=95.0, rep_high=155.0,
        rep_direction="low_first",
        phase_a_label="Squatting", phase_b_label="Rising"
    ),
    # WRISTS — angle is 0-180 (clamped by angle.py).
    # Neutral wrist ≈ 180 (straight forearm-to-finger), but clamping means neutral ≈ 170-180.
    # Flexion bends the wrist → angle decreases from ~170 toward ~100.
    # Ranges adjusted to fit within the 0-180 output.
    "right_wrist_flexion": ExerciseConfig(
        key="right_wrist_flexion", title="R Wrist Flex", side="right",
        description="Flex wrist. Neutral ≈ 170-180°, flexion reduces angle.",
        triplet=("right_elbow", "right_wrist", "right_index"),
        target_min=100.0, target_max=175.0,
        low_hint="Extend wrist back.", high_hint="Flex wrist more.",
        rep_low=120.0, rep_high=165.0,
        rep_direction="low_first",
        phase_a_label="Flexing", phase_b_label="Extending"
    ),
    "left_wrist_flexion": ExerciseConfig(
        key="left_wrist_flexion", title="L Wrist Flex", side="left",
        description="Flex wrist. Neutral ≈ 170-180°, flexion reduces angle.",
        triplet=("left_elbow", "left_wrist", "left_index"),
        target_min=100.0, target_max=175.0,
        low_hint="Extend wrist back.", high_hint="Flex wrist more.",
        rep_low=120.0, rep_high=165.0,
        rep_direction="low_first",
        phase_a_label="Flexing", phase_b_label="Extending"
    ),
    # HIPS — raise knee (angle decreases), lower (angle increases)
    "right_hip_flexion": ExerciseConfig(
        key="right_hip_flexion", title="R Hip Flexion", side="right",
        description="Raise knee toward chest.",
        triplet=("right_shoulder", "right_hip", "right_knee"),
        target_min=95.0, target_max=170.0,
        low_hint="Lower leg.", high_hint="Raise knee higher.",
        rep_low=110.0, rep_high=155.0,
        rep_direction="low_first",
        phase_a_label="Lifting", phase_b_label="Lowering"
    ),
    "left_hip_flexion": ExerciseConfig(
        key="left_hip_flexion", title="L Hip Flexion", side="left",
        description="Raise knee toward chest.",
        triplet=("left_shoulder", "left_hip", "left_knee"),
        target_min=95.0, target_max=170.0,
        low_hint="Lower leg.", high_hint="Raise knee higher.",
        rep_low=110.0, rep_high=155.0,
        rep_direction="low_first",
        phase_a_label="Lifting", phase_b_label="Lowering"
    ),
}

_LEGACY_EXERCISE_ALIASES = {
    "elbow_flexion": "right_elbow_flexion",
    "shoulder_raise": "right_shoulder_abduction",
    "wrist_flexion": "right_wrist_flexion",
    "hip_flexion": "right_hip_flexion",
    "squat": "right_squat",
}


def get_exercise_config(exercise_key: str) -> ExerciseConfig:
    resolved_key = _LEGACY_EXERCISE_ALIASES.get(exercise_key, exercise_key)
    return EXERCISE_CONFIGS[resolved_key]
