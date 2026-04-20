import unittest

import cv2


class TestCameraModule(unittest.TestCase):
    def test_opencv_available(self):
        self.assertTrue(hasattr(cv2, "VideoCapture"))


if __name__ == "__main__":
    unittest.main()