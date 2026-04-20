from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ExerciseConfig:
    key: str
    title: str
    description: str
    triplet: Tuple[str, str, str]
    target_min: float
    target_max: float
    low_hint: str
    high_hint: str
    rep_low: float
    rep_high: float
    rom_try_threshold: float
    rom_good_threshold: float


EXERCISE_CONFIGS: Dict[str, ExerciseConfig] = {
    "elbow_flexion": ExerciseConfig(
        key="elbow_flexion",
        title="Elbow Flexion",
        description="Bend and extend your right elbow in a controlled range.",
        triplet=("right_shoulder", "right_elbow", "right_wrist"),
        target_min=45.0,
        target_max=165.0,
        low_hint="Open your elbow a little more.",
        high_hint="Bend your elbow further.",
        rep_low=65.0,
        rep_high=145.0,
        rom_try_threshold=35.0,
        rom_good_threshold=70.0,
    ),
    "squat": ExerciseConfig(
        key="squat",
        title="Squat",
        description="Lower and rise smoothly while keeping knee tracking stable.",
        triplet=("right_hip", "right_knee", "right_ankle"),
        target_min=70.0,
        target_max=170.0,
        low_hint="Do not go too deep; keep control.",
        high_hint="Lower your hips a bit more.",
        rep_low=95.0,
        rep_high=155.0,
        rom_try_threshold=30.0,
        rom_good_threshold=60.0,
    ),
    "shoulder_raise": ExerciseConfig(
        key="shoulder_raise",
        title="Shoulder Raise",
        description="Raise your right arm and lower it with control.",
        triplet=("right_elbow", "right_shoulder", "right_hip"),
        target_min=35.0,
        target_max=120.0,
        low_hint="Lower your arm slightly to stay in control.",
        high_hint="Raise your arm higher.",
        rep_low=50.0,
        rep_high=105.0,
        rom_try_threshold=25.0,
        rom_good_threshold=55.0,
    ),
}


def get_exercise_config(exercise_key: str) -> ExerciseConfig:
    return EXERCISE_CONFIGS[exercise_key]
