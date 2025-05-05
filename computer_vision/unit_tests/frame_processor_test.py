import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2

# Import the FrameProcessor class from its module path
from src.Classes.frame_processor import FrameProcessor

class TestFrameProcessor(unittest.TestCase):
    def setUp(self):
        """
        Create a dummy frame and instantiate the processor.
        The dummy frame simulates a 480×854 BGR image filled with mid‑gray values.
        """
        self.sample_frame = np.ones((480, 854, 3), dtype=np.uint8) * 127
        self.processor = FrameProcessor()

    @patch('src.Classes.frame_processor.cv2.VideoCapture')
    def test_open_successful(self, mock_VideoCapture):
        """
        Verify that open() correctly initializes the camera source,
        sets the desired resolution, and reads the first frame without errors.
        """
        # Configure the VideoCapture mock to behave as if the camera opened OK
        mock_vc = MagicMock()
        mock_vc.isOpened.return_value = True
        mock_vc.read.return_value = (True, self.sample_frame)
        mock_VideoCapture.return_value = mock_vc

        # Should not raise an exception
        self.processor.open()

        # Confirm that VideoCapture was called with default src=0
        mock_VideoCapture.assert_called_with(0)
        # Confirm that resolution settings were applied
        mock_vc.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 854)
        mock_vc.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # Confirm that read() was invoked to fetch the first frame
        mock_vc.read.assert_called()

    @patch('src.Classes.frame_processor.cv2.VideoCapture')
    def test_open_failure_no_device(self, mock_VideoCapture):
        """
        If isOpened() returns False, open() should raise a RuntimeError
        indicating that the camera could not be opened.
        """
        mock_vc = MagicMock()
        mock_vc.isOpened.return_value = False
        mock_VideoCapture.return_value = mock_vc

        with self.assertRaises(RuntimeError):
            self.processor.open()

    @patch('src.Classes.frame_processor.cv2.VideoCapture')
    def test_open_failure_read_fail(self, mock_VideoCapture):
        """
        If isOpened() succeeds but the first read() fails (returns False),
        open() must raise a RuntimeError indicating read failure.
        """
        mock_vc = MagicMock()
        mock_vc.isOpened.return_value = True
        mock_vc.read.return_value = (False, None)
        mock_VideoCapture.return_value = mock_vc

        with self.assertRaises(RuntimeError):
            self.processor.open()

    def test_process_frame(self):
        """
        Directly test the internal _process_frame method:
        - Result must be a 2D array (grayscale, blurred).
        - Dimensions should match the input frame width/height.
        """
        processed = self.processor._process_frame(self.sample_frame)
        self.assertEqual(processed.shape, (480, 854))
        self.assertEqual(len(processed.shape), 2)

    @patch('src.Classes.frame_processor.cv2.VideoCapture')
    def test_get_frame_successful(self, mock_VideoCapture):
        """
        After a successful open(), get_frame() should return (True, jpeg_bytes).
        We simulate two reads: the first for open(), the second for get_frame().
        """
        mock_vc = MagicMock()
        mock_vc.isOpened.return_value = True
        mock_vc.read.side_effect = [
            (True, self.sample_frame),  # consumed by open()
            (True, self.sample_frame)   # consumed by get_frame()
        ]
        mock_VideoCapture.return_value = mock_vc

        self.processor.open()
        ok, jpeg = self.processor.get_frame()

        self.assertTrue(ok)
        self.assertIsInstance(jpeg, bytes)

    @patch('src.Classes.frame_processor.cv2.VideoCapture')
    def test_get_frame_failure(self, mock_VideoCapture):
        """
        If get_frame() encounters a read() that returns False, it should
        return (False, None) rather than throwing an exception.
        """
        mock_vc = MagicMock()
        mock_vc.isOpened.return_value = True
        mock_vc.read.side_effect = [
            (True, self.sample_frame),  # open()
            (False, None)               # get_frame()
        ]
        mock_VideoCapture.return_value = mock_vc

        self.processor.open()
        ok, jpeg = self.processor.get_frame()

        self.assertFalse(ok)
        self.assertIsNone(jpeg)

    @patch('src.Classes.frame_processor.cv2.VideoCapture')
    def test_frame_generator(self, mock_VideoCapture):
        """
        The frame_generator should yield JPEG frames in MJPEG multipart format
        until read() returns False. We simulate:
        - one read for open(),
        - two successful reads for generator,
        - one final False to stop iteration.
        """
        mock_vc = MagicMock()
        mock_vc.isOpened.return_value = True
        mock_vc.read.side_effect = [
            (True, self.sample_frame),  # open()
            (True, self.sample_frame),  # first yield
            (True, self.sample_frame),  # second yield
            (False, None)               # stop
        ]
        mock_VideoCapture.return_value = mock_vc

        self.processor.open()
        frames = list(self.processor.frame_generator())

        # Should produce exactly two frames before stopping
        self.assertEqual(len(frames), 2)
        for frame_bytes in frames:
            # Each chunk must start with the multipart boundary and headers
            self.assertTrue(frame_bytes.startswith(b'--frame\r\n'))
            self.assertIn(b'Content-Type: image/jpeg\r\n\r\n', frame_bytes)

if __name__ == '__main__':
    unittest.main()
