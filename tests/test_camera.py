import unittest

try:
    import cv2
except ModuleNotFoundError:
    cv2 = None


class TestCameraModule(unittest.TestCase):
    @unittest.skipIf(cv2 is None, "opencv-python is not installed in this environment")
    def test_opencv_available(self):
        self.assertTrue(hasattr(cv2, "VideoCapture"))


if __name__ == "__main__":
    unittest.main()
