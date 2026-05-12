from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import time
import statistics

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
    phase: str          # Anatomically labeled phase (e.g., "Bending", "Raising")
    speed_warning: bool # True if angular velocity exceeds config.max_speed
    jerk_warning: bool  # True if movement variance is too high


class ExerciseEvaluator:
    def __init__(self, config: ExerciseConfig):
        self.config = config
        self.rom_tracker = MovementAnalyzer(filter_alpha=0.3)
        self.reps = 0
        self._phase = "Ready"
        self._prev_smoothed_angle = None
        self._prev_time = None
        self._speed_warning = False
        self._jerk_warning = False
        # Bug 4 fix: Rolling velocity buffer for jerkiness detection
        self._velocity_buffer: deque = deque(maxlen=10)

    def reset(self) -> None:
        self.rom_tracker = MovementAnalyzer(filter_alpha=0.3)
        self.reps = 0
        self._phase = "Ready"
        self._prev_smoothed_angle = None
        self._prev_time = None
        self._speed_warning = False
        self._jerk_warning = False
        self._velocity_buffer.clear()

    def update_config(self, config: ExerciseConfig, reset_state: bool = True) -> None:
        self.config = config
        if reset_state:
            self.reset()

    def evaluate(self, coords: Dict[str, tuple]) -> Optional[ExerciseMetrics]:
        point_names = self.config.triplet
        if not all(name in coords for name in point_names):
            return None

        now = time.time()
        angle = calculate_joint_angle(
            coords[point_names[0]],
            coords[point_names[1]],
            coords[point_names[2]],
        )

        # 2. ROM update (EMA-smoothed internally)
        rom, _, _ = self.rom_tracker.update(angle)
        smoothed_angle = self.rom_tracker.smoothed_angle

        # 1. Speed Tracking - Bug 1 fix: use config.max_speed; Bug 5 fix: use smoothed angle
        self._speed_warning = False
        self._jerk_warning = False
        if self._prev_smoothed_angle is not None and self._prev_time is not None:
            dt = now - self._prev_time
            if dt > 0:
                velocity = abs(smoothed_angle - self._prev_smoothed_angle) / dt  # deg/sec

                # Bug 1 fix: use config's max_speed (deg/sec) instead of hardcoded value
                if velocity > self.config.max_speed:
                    self._speed_warning = True

                # Bug 4 fix: jerkiness detection via velocity variance
                self._velocity_buffer.append(velocity)
                if len(self._velocity_buffer) >= 5:
                    try:
                        vel_variance = statistics.variance(self._velocity_buffer)
                        if vel_variance > self.config.jerk_threshold ** 2:
                            self._jerk_warning = True
                    except statistics.StatisticsError:
                        pass

        self._prev_smoothed_angle = smoothed_angle
        self._prev_time = now

        # 3. Rep counting - Bug 3 fix: direction-aware; Bug 6 fix: clean Ready transition
        self._update_reps(smoothed_angle)

        # 4. Status & Hint
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
            phase=self._phase,
            speed_warning=self._speed_warning,
            jerk_warning=self._jerk_warning
        )

    def _get_rom_feedback(self, rom: float) -> str:
        """Percentage-based ROM feedback relative to target span."""
        target_span = self.config.target_max - self.config.target_min
        if target_span <= 0:
            return "Poor ROM"

        percent = (rom / target_span) * 100
        if percent >= 70:
            return "Good ROM"
        if percent >= 40:
            return "Fair ROM"
        return "Poor ROM"

    def _update_reps(self, angle: float) -> None:
        """
        Direction-aware rep state machine.
        
        "low_first": Ready -> phase_a (angle <= rep_low) -> phase_b (angle >= rep_high) -> rep++ -> Ready
        "high_first": Ready -> phase_a (angle >= rep_high) -> phase_b (angle <= rep_low) -> rep++ -> Ready
        """
        cfg = self.config
        a_label = cfg.phase_a_label
        b_label = cfg.phase_b_label

        if cfg.rep_direction == "low_first":
            enter_a = angle <= cfg.rep_low
            enter_b = angle >= cfg.rep_high
        else:  # "high_first"
            enter_a = angle >= cfg.rep_high
            enter_b = angle <= cfg.rep_low

        if self._phase == "Ready":
            if enter_a:
                self._phase = a_label
        elif self._phase == a_label:
            if enter_b:
                self.reps += 1
                self._phase = b_label
        elif self._phase == b_label:
            if not enter_b:
                self._phase = "Ready"
        elif self._phase not in ("Ready", a_label, b_label):
            self._phase = "Ready"


