from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from angle.angle import calculate_joint_angle
from movement.analysis import MovementAnalyzer
from movement.exercises import ExerciseConfig


@dataclass
class ExerciseMetrics:
    angle: float
    rom: float
    reps: int
    status: str
    rom_feedback: str
    hint: str
    joint_point: Tuple[int, int]


class ExerciseEvaluator:
    def __init__(self, config: ExerciseConfig):
        self.config = config
        self.rom_tracker = MovementAnalyzer()
        self.reps = 0
        self._phase = "high"

    def update_config(self, config: ExerciseConfig) -> None:
        if config.key == self.config.key:
            return

        self.config = config
        self.rom_tracker = MovementAnalyzer()
        self.reps = 0
        self._phase = "high"

    def evaluate(self, coords: Dict[str, tuple]) -> Optional[ExerciseMetrics]:
        point_names = self.config.triplet
        if not all(name in coords for name in point_names):
            return None

        angle = calculate_joint_angle(
            coords[point_names[0]],
            coords[point_names[1]],
            coords[point_names[2]],
        )

        rom, _, _ = self.rom_tracker.update(angle)
        self._update_reps(angle)

        if self.config.target_min <= angle <= self.config.target_max:
            status = "Correct"
            hint = "Good posture. Keep a smooth rhythm."
        elif angle < self.config.target_min:
            status = "Incorrect"
            hint = self.config.low_hint
        else:
            status = "Incorrect"
            hint = self.config.high_hint

        return ExerciseMetrics(
            angle=angle,
            rom=rom,
            reps=self.reps,
            status=status,
            rom_feedback=self._get_rom_feedback(rom),
            hint=hint,
            joint_point=coords[point_names[1]],
        )

    def _get_rom_feedback(self, rom: float) -> str:
        if rom >= self.config.rom_good_threshold:
            return "Good Range of Motion"
        if rom >= self.config.rom_try_threshold:
            return "Try to extend further"
        return "Incomplete movement"

    def _update_reps(self, angle: float) -> None:
        if self._phase == "high" and angle <= self.config.rep_low:
            self._phase = "low"
        elif self._phase == "low" and angle >= self.config.rep_high:
            self.reps += 1
            self._phase = "high"
