import unittest

from movement.evaluator import ExerciseEvaluator
from movement.exercises import get_exercise_config


class TestExerciseEvaluator(unittest.TestCase):
    def test_elbow_flexion_correct_status(self):
        evaluator = ExerciseEvaluator(get_exercise_config("elbow_flexion"))
        coords = {
            "right_shoulder": (0, 1),
            "right_elbow": (0, 0),
            "right_wrist": (1, 0),
        }

        metrics = evaluator.evaluate(coords)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.status, "Correct")
        self.assertEqual(metrics.rom_feedback, "Incomplete movement")
        self.assertEqual(metrics.joint_point, (0, 0))

    def test_repetition_count_increments(self):
        evaluator = ExerciseEvaluator(get_exercise_config("elbow_flexion"))

        # Low-angle posture (flexion) to transition phase.
        coords_low = {
            "right_shoulder": (0, 1),
            "right_elbow": (0, 0),
            "right_wrist": (1, 1),
        }

        # High-angle posture (extension) to complete one rep.
        coords_high = {
            "right_shoulder": (-1, 0),
            "right_elbow": (0, 0),
            "right_wrist": (1, 0),
        }

        evaluator.evaluate(coords_low)
        metrics = evaluator.evaluate(coords_high)

        self.assertIsNotNone(metrics)
        self.assertGreaterEqual(metrics.reps, 1)

    def test_rom_feedback_progression(self):
        evaluator = ExerciseEvaluator(get_exercise_config("elbow_flexion"))

        # About 90 deg
        coords_mid = {
            "right_shoulder": (0, 1),
            "right_elbow": (0, 0),
            "right_wrist": (1, 0),
        }

        # About 45 deg
        coords_low = {
            "right_shoulder": (0, 1),
            "right_elbow": (0, 0),
            "right_wrist": (1, 1),
        }

        m1 = evaluator.evaluate(coords_mid)
        self.assertIsNotNone(m1)
        self.assertEqual(m1.rom_feedback, "Incomplete movement")

        m2 = evaluator.evaluate(coords_low)
        self.assertIsNotNone(m2)
        self.assertEqual(m2.rom_feedback, "Try to extend further")

        coords_high = {
            "right_shoulder": (-1, 0),
            "right_elbow": (0, 0),
            "right_wrist": (1, 0),
        }
        m3 = evaluator.evaluate(coords_high)
        self.assertIsNotNone(m3)
        self.assertEqual(m3.rom_feedback, "Good Range of Motion")


if __name__ == "__main__":
    unittest.main()
