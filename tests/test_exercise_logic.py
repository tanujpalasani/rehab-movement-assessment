import unittest

from movement.evaluator import ExerciseEvaluator
from movement.exercises import get_exercise_config


class TestExerciseEvaluator(unittest.TestCase):
    def test_legacy_exercise_alias_resolves(self):
        config = get_exercise_config("elbow_flexion")
        self.assertEqual(config.key, "right_elbow_flexion")

    def test_elbow_flexion_correct_status(self):
        evaluator = ExerciseEvaluator(get_exercise_config("right_elbow_flexion"))
        coords = {
            "right_shoulder": (0, 1),
            "right_elbow": (0, 0),
            "right_wrist": (1, 0),
        }

        metrics = evaluator.evaluate(coords)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.status, "Correct")
        self.assertEqual(metrics.rom_feedback, "Poor ROM")
        self.assertEqual(metrics.joint_point, (0, 0))
        self.assertEqual(metrics.phase, "Ready")

    def test_repetition_count_increments(self):
        evaluator = ExerciseEvaluator(get_exercise_config("right_elbow_flexion"))

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

        for _ in range(8):
            evaluator.evaluate(coords_low)
        metrics = None
        for _ in range(12):
            metrics = evaluator.evaluate(coords_high)

        self.assertIsNotNone(metrics)
        self.assertGreaterEqual(metrics.reps, 1)
        self.assertEqual(metrics.phase, "Straightening")

    def test_rom_feedback_progression(self):
        evaluator = ExerciseEvaluator(get_exercise_config("right_elbow_flexion"))

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
        self.assertEqual(m1.rom_feedback, "Poor ROM")

        for _ in range(8):
            m2 = evaluator.evaluate(coords_low)
        self.assertIsNotNone(m2)
        self.assertEqual(m2.rom_feedback, "Poor ROM")

        coords_high = {
            "right_shoulder": (-1, 0),
            "right_elbow": (0, 0),
            "right_wrist": (1, 0),
        }
        fair_seen = False
        m3 = None
        for _ in range(12):
            m3 = evaluator.evaluate(coords_high)
            if m3.rom_feedback == "Fair ROM":
                fair_seen = True

        self.assertIsNotNone(m3)
        self.assertTrue(fair_seen)
        self.assertEqual(m3.rom_feedback, "Good ROM")


if __name__ == "__main__":
    unittest.main()
