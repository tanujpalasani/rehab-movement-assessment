import unittest

from angle.angle import calculate_angle
from feedback.feedback import generate_feedback
from movement.analysis import MovementAnalyzer


class TestAngle(unittest.TestCase):
    def test_calculate_angle_right_angle(self):
        coords = {
            "shoulder": (0, 1),
            "elbow": (0, 0),
            "wrist": (1, 0),
        }
        angle = calculate_angle(coords)
        self.assertAlmostEqual(angle, 90.0, places=4)

    def test_calculate_angle_missing_coordinate(self):
        coords = {
            "shoulder": (0, 1),
            "elbow": (0, 0),
        }
        with self.assertRaises(ValueError):
            calculate_angle(coords)


class TestMovementAnalyzer(unittest.TestCase):
    def test_update_tracks_rom(self):
        analyzer = MovementAnalyzer()

        rom1, min_a1, max_a1 = analyzer.update(80)
        rom2, min_a2, max_a2 = analyzer.update(120)
        rom3, min_a3, max_a3 = analyzer.update(70)

        self.assertEqual((rom1, min_a1, max_a1), (0, 80, 80))
        self.assertEqual((rom2, min_a2, max_a2), (40, 80, 120))
        self.assertEqual((rom3, min_a3, max_a3), (50, 70, 120))


class TestFeedback(unittest.TestCase):
    def test_feedback_bands(self):
        self.assertEqual(generate_feedback(30), "Very Limited Movement")
        self.assertEqual(generate_feedback(75), "Needs Improvement")
        self.assertEqual(generate_feedback(120), "Good Movement")
        self.assertEqual(generate_feedback(170), "Excellent Movement")


if __name__ == "__main__":
    unittest.main()