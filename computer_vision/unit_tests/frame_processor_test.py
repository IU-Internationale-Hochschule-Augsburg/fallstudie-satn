import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import cv2

from src.Classes.FrameProcessor import FrameProcessor

class TestFrameProcessor(unittest.TestCase):
    def test_init_defaults(self):
        fp = FrameProcessor()
        self.assertEqual(fp.width, 1280)
        self.assertEqual(fp.height, 720)
        self.assertEqual(fp.alpha, 2.0)
        self.assertEqual(fp.beta, 0)
        self.assertEqual(fp.blur_ksize, 3)
        self.assertIsNone(fp.picam2)

    @patch('src.Classes.FrameProcessor.Picamera2')
    def test_open_initializes_and_starts(self, mock_picam_cls):
        mock_picam = MagicMock()
        mock_picam_cls.return_value = mock_picam
        fp = FrameProcessor()
        fp.open()
        mock_picam_cls.assert_called_once()
        mock_picam.start.assert_called_once()
        self.assertIs(fp.picam2, mock_picam)

    @patch('src.Classes.FrameProcessor.Picamera2')
    def test_open_idempotent(self, mock_picam_cls):
        fp = FrameProcessor()
        fp.picam2 = MagicMock()
        fp.open()  # should do nothing
        mock_picam_cls.assert_not_called()

    def test_release_when_open(self):
        fp = FrameProcessor()
        mock_picam = MagicMock()
        fp.picam2 = mock_picam
        fp.release()
        mock_picam.stop.assert_called_once()
        mock_picam.close.assert_called_once()
        self.assertIsNone(fp.picam2)

    def test_release_when_none(self):
        fp = FrameProcessor()
        fp.picam2 = None
        # should not raise
        fp.release()
        self.assertIsNone(fp.picam2)

    def test__process_frame(self):
        # create a small RGB image (3x3)
        img = np.zeros((3,3,3), dtype=np.uint8)
        # set a pixel to white
        img[1,1] = [255,255,255]
        # use blur_ksize=1 to avoid median blur effect
        fp = FrameProcessor(alpha=1.0, beta=0, blur_ksize=1)
        out = fp._process_frame(img)
        # output should be grayscale shape (3,3)
        self.assertEqual(out.shape, (3,3))
        # center pixel should be 255 after conversion and blur
        self.assertEqual(out[1,1], 255)

    def test_get_frame_no_camera(self):
        fp = FrameProcessor()
        ok, data = fp.get_frame()
        self.assertFalse(ok)
        self.assertIsNone(data)

    def test_get_frame_capture_exception(self):
        fp = FrameProcessor()
        mock_picam = MagicMock()
        mock_picam.capture_array.side_effect = Exception("Kamera-Fehler")
        fp.picam2 = mock_picam
        ok, data = fp.get_frame()
        self.assertFalse(ok)
        self.assertIsNone(data)
        # ensure release cleared picam2
        self.assertIsNone(fp.picam2)

    def test_get_frame_capture_none(self):
        fp = FrameProcessor()
        mock_picam = MagicMock()
        mock_picam.capture_array.return_value = None
        fp.picam2 = mock_picam
        ok, data = fp.get_frame()
        self.assertFalse(ok)
        self.assertIsNone(data)

    def test_get_frame_success_no_perspective(self):
        fp = FrameProcessor()
        # create a BGR grayscale frame for simplicity
        frame = np.ones((5,5,3), dtype=np.uint8) * 100
        mock_picam = MagicMock()
        mock_picam.capture_array.return_value = frame
        fp.picam2 = mock_picam
        ok, data = fp.get_frame()
        self.assertTrue(ok)
        # no rectangle yields None
        self.assertIsNone(data)

    def test_frame_generator(self):
        fp = FrameProcessor()
        # stub get_frame: first False, then True, then StopIteration
        seq = [(False, None), (True, b'data'), StopIteration()]
        fp.get_frame = MagicMock(side_effect=seq)
        fp.release = MagicMock()
        gen = fp.frame_generator()
        # get first yielded frame
        frame_bytes = next(gen)
        expected = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + b'data' + b'\r\n'
        self.assertEqual(frame_bytes, expected)
        # next should raise StopIteration
        with self.assertRaises(StopIteration):
            next(gen)
        # release called in finally
        fp.release.assert_called_once()

    def test_fix_perspective_no_contour(self):
        fp = FrameProcessor()
        # blank image
        img = np.zeros((10,10), dtype=np.uint8)
        out = fp.fix_perspective(img)
        self.assertIsNone(out)

    def test_fix_perspective_with_rectangle(self):
        fp = FrameProcessor()
        # create binary image with white rectangle
        img = np.zeros((500,500), dtype=np.uint8)
        cv2.rectangle(img, (50,50), (150,100), 255, -1)
        warped = fp.fix_perspective(img)
        # warped should have shape (400,300)
        self.assertIsNotNone(warped)
        self.assertEqual(warped.shape, (400,300))

    def test_order_points(self):
        fp = FrameProcessor()
        pts = np.array([[1,2],[3,4],[5,0],[0,0]], dtype="float32")
        rect = fp.order_points(pts)
        # rect[0] is top-left (min sum)
        sums = rect.sum(axis=1)
        self.assertTrue(np.argmin(sums) == 0)
        # rect[2] is bottom-right (max sum)
        self.assertTrue(np.argmax(sums) == 2)
        # rect has shape (4,2)
        self.assertEqual(rect.shape, (4,2))

if __name__ == '__main__':
    unittest.main()
