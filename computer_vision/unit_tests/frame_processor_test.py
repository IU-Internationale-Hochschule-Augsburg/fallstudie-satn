import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
import threading

# Import the FrameProcessor class
from src.Classes.FrameProcessor import FrameProcessor, Picamera2

class TestFrameProcessor(unittest.TestCase):
    def setUp(self):
        self.height = 720
        self.width = 1280
        self.sample_frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 127
        self.processor = FrameProcessor()

        patcher = patch('src.Classes.FrameProcessor.Picamera2')
        self.mock_picam2_class = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_picam2 = MagicMock()
        self.mock_picam2.create_preview_configuration.return_value = 'config'
        self.mock_picam2.capture_array.return_value = self.sample_frame
        self.mock_picam2_class.return_value = self.mock_picam2

    def test_open_initializes_camera(self):
        self.processor.open()
        self.mock_picam2 = MagicMock()
        self.mock_picam2_class.assert_called_once()
        self.mock_picam2.create_preview_configuration.assert_called_with(
            main={"format": 'RGB888', "size": (self.processor.width, self.processor.height)}
        )
        self.mock_picam2.configure.assert_called_once_with('config')
        self.mock_picam2.start.assert_called_once()
        self.assertTrue(self.processor.running)

    def test_capture_loop_updates_frame(self):
        self.mock_picam2 = MagicMock()
        self.processor.picam2 = self.mock_picam2
        self.processor.running = True
        self.mock_picam2.capture_array.side_effect = [self.sample_frame, Exception("Stop")]
        with self.assertRaises(Exception):
            self.processor._capture_loop()
        self.assertTrue(np.array_equal(self.processor.frame, self.sample_frame))

    def test_release_stops_camera(self):
        self.mock_picam2 = MagicMock()
        self.processor.running = True
        self.processor.picam2 = self.mock_picam2

        self.processor.release()

        self.assertFalse(self.processor.running)
        self.mock_picam2.stop.assert_called_once()
        self.assertIsNone(self.processor.picam2)

    def test_process_frame_outputs_grayscale_image(self):
        result = self.processor._process_frame(self.sample_frame)
        self.assertEqual(result.ndim, 2)
        self.assertEqual(result.shape, (self.height, self.width))
        self.assertTrue((0 <= result).all() and (result <= 255).all())

    def test_get_frame_raises_if_not_opened(self):
        with self.assertRaises(RuntimeError):
            self.processor.get_frame()

    def test_get_frame_returns_false_if_no_frame(self):
        self.processor.running = True
        self.processor.frame = None
        ok, jpeg = self.processor.get_frame()
        self.assertFalse(ok)
        self.assertIsNone(jpeg)

    def test_get_frame_returns_jpeg_if_successful(self):
        self.processor.running = True
        self.processor.frame = self.sample_frame
        ok, jpeg = self.processor.get_frame()
        self.assertTrue(ok)
        self.assertTrue(jpeg.startswith(b'\xff\xd8') and jpeg.endswith(b'\xff\xd9'))

    def test_get_frame_returns_false_if_encoding_fails(self):
        with patch('src.Classes.FrameProcessor.cv2.imencode', return_value=(False, None)):
            self.processor.running = True
            self.processor.frame = self.sample_frame
            ok, jpeg = self.processor.get_frame()
            self.assertFalse(ok)
            self.assertIsNone(jpeg)

    def test_frame_generator_yields_and_releases(self):
        self.processor.running = True

        sequence = [(True, b'image1'), (True, b'image2')]
        self.processor.get_frame = MagicMock(side_effect=sequence + [Exception("stop")])

        gen = self.processor.frame_generator()

        frame1 = next(gen)
        self.assertIn(b'image1', frame1)
        frame2 = next(gen)
        self.assertIn(b'image2', frame2)

        with self.assertRaises(Exception):
            next(gen)

        self.assertFalse(self.processor.running)

if __name__ == '__main__':
    unittest.main()
