import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2

from src.Classes.ObjectDetection.ObjectDetection import ObjectDetection


class TestObjectDetection(unittest.TestCase):
    def setUp(self):
        # Picamera2 patchen, damit es beim FrameProcessor-Konstruktor nicht crasht
        patcher_picamera2 = patch('src.Classes.FrameProcessor.Picamera2')
        self.mock_picamera2_cls = patcher_picamera2.start()
        self.addCleanup(patcher_picamera2.stop)
        self.mock_picamera2_instance = MagicMock()
        self.mock_picamera2_cls.return_value = self.mock_picamera2_instance

        # FrameProcessor patchen (falls nötig)
        patcher_fp = patch('src.Classes.FrameProcessor.FrameProcessor')
        self.mock_frame_processor_cls = patcher_fp.start()
        self.addCleanup(patcher_fp.stop)
        self.mock_frame_processor_instance = MagicMock()
        self.mock_frame_processor_cls.return_value = self.mock_frame_processor_instance

        # Dein ObjektDetection-Objekt initialisieren
        self.obj_det = ObjectDetection()
        # zusätzlich: mock für Kamera-Objekt, falls dein ObjectDetection das verwendet
        self.mock_camera = MagicMock()
        # Falls ObjectDetection.camera = self.mock_camera gemacht werden soll:
        self.obj_det.camera = self.mock_camera

    @patch('cv2.threshold')
    @patch('cv2.findContours')
    def test_get_zumo_position_only_contours(self, mock_findContours, mock_threshold):
        # Setup mocks
        img = np.zeros((10, 10), dtype=np.uint8)
        mock_threshold.return_value = (None, np.ones((10, 10), dtype=np.uint8) * 255)
        # Provide two simple contours
        cnt1 = np.array([[[0, 0]], [[1, 0]], [[1, 1]], [[0, 1]]])
        cnt2 = np.array([[[2, 2]], [[3, 2]], [[3, 3]], [[2, 3]]])
        mock_findContours.return_value = ([cnt1, cnt2], None)

        # only_contours=True returns top contours directly
        result = self.obj_det.get_zumo_position(img, only_contours=True)
        self.assertEqual(result, [cnt1, cnt2])

    @patch('cv2.minAreaRect')
    @patch('cv2.threshold')
    @patch('cv2.findContours')
    def test_get_zumo_position_returns_position(self, mock_findContours, mock_threshold, mock_minAreaRect):
        img = np.zeros((10, 10), dtype=np.uint8)
        mock_threshold.return_value = (None, np.ones((10, 10), dtype=np.uint8) * 255)
        # Two contours for combination
        cnt1 = np.array([[[0, 0]], [[1, 0]], [[1, 1]], [[0, 1]]])
        cnt2 = np.array([[[2, 2]], [[3, 2]], [[3, 3]], [[2, 3]]])
        mock_findContours.return_value = ([cnt1, cnt2], None)

        # Mock minAreaRect results with controlled values to pass fitness score test
        mock_minAreaRect.side_effect = [
            ((0, 0), (10, 10), 10),
            ((0, 0), (10, 10), 10),
            ((0, 0), (10, 10), 10),
            ((0, 0), (10, 10), 10),
        ]

        result = self.obj_det.get_zumo_position(img, only_contours=False)
        self.assertIsInstance(result, dict)
        self.assertIn('xCoord', result)
        self.assertIn('yCoord', result)
        self.assertIn('dx', result)
        self.assertIn('dy', result)

    @patch('cv2.threshold')
    @patch('cv2.findContours')
    def test_get_zumo_position_no_contours(self, mock_findContours, mock_threshold):
        img = np.zeros((10, 10), dtype=np.uint8)
        mock_threshold.return_value = (None, np.ones((10, 10), dtype=np.uint8) * 255)
        mock_findContours.return_value = ([], None)

        result = self.obj_det.get_zumo_position(img)
        self.assertIsNone(result)

    @patch.object(ObjectDetection, 'get_zumo_position')
    @patch('cv2.threshold')
    @patch('cv2.findContours')
    def test_get_object_position_filters_and_returns_objects(self, mock_findContours, mock_threshold,
                                                             mock_get_zumo_position):
        img = np.zeros((20, 20), dtype=np.uint8)

        # Mock Zumo data (simulate position)
        mock_get_zumo_position.return_value = {'xCoord': 5, 'yCoord': 5, 'dx': 10, 'dy': 10}

        # Mock threshold and contours with 3 contours
        mock_threshold.return_value = (None, np.ones((20, 20), dtype=np.uint8) * 255)
        cnt1 = np.array([[[0, 0]], [[1, 0]], [[1, 1]], [[0, 1]]])  # Small contour
        cnt2 = np.array([[[6, 6]], [[7, 6]], [[7, 7]], [[6, 7]]])  # Close to Zumo -> exclude
        cnt3 = np.array([[[20, 20]], [[22, 20]], [[22, 22]], [[20, 22]]])  # Large contour, keep

        mock_findContours.return_value = ([cnt1, cnt2, cnt3], None)

        # Patch boundingRect to return sizes for each contour
        with patch('cv2.boundingRect') as mock_boundingRect:
            mock_boundingRect.side_effect = [
                (0, 0, 1, 1),  # cnt1 area 1 < min_area
                (6, 6, 2, 2),  # cnt2 close to Zumo, should exclude
                (20, 20, 2, 2)  # cnt3 area 4 > min_area=3 -> keep
            ]

            objects = self.obj_det.get_object_position(img, min_area=3)
            self.assertEqual(len(objects), 1)
            self.assertEqual(objects[0]['xCoord'], 20)

    def test_crop_image_with_dark_frame(self):
        # Create gray image with dark border
        img = np.ones((10, 10), dtype=np.uint8) * 255
        img[0, :] = 0
        img[:, 0] = 0
        img[9, :] = 0
        img[:, 9] = 0

        cropped = self.obj_det.crop_image(img, dark_thresh=10)
        # Result should be smaller than original due to crop
        self.assertTrue(cropped.shape[0] < img.shape[0])
        self.assertTrue(cropped.shape[1] < img.shape[1])

    def test_crop_image_no_dark_frame(self):
        img = np.ones((10, 10), dtype=np.uint8) * 255
        cropped = self.obj_det.crop_image(img, dark_thresh=10)
        self.assertTrue(np.array_equal(cropped, img))

    def test_crop_image_invalid_input(self):
        with self.assertRaises(ValueError):
            self.obj_det.crop_image(None)
        with self.assertRaises(ValueError):
            self.obj_det.crop_image(np.zeros((10, 10, 3), dtype=np.uint8))  # 3D image

    def test_identify_features_returns_correct_dict(self):
        cnt = np.array([[[0, 0]], [[2, 0]], [[2, 2]], [[0, 2]]])
        features = self.obj_det.identify_features(cnt)a
        self.assertEqual(features['area'], 9.0)
        self.assertAlmostEqual(features['aspect_ratio'], 1.0)
        self.assertEqual(features['width'], 3)
        self.assertEqual(features['height'], 3)

    @patch.object(ObjectDetection, 'get_object_position')
    @patch.object(ObjectDetection, 'get_zumo_position')
    def test_handle_object_detection_from_source(self, mock_get_zumo_position, mock_get_object_position):
        self.mock_camera.get_frame.return_value = (True, np.ones((10, 10), dtype=np.uint8))
        mock_get_object_position.return_value = ['object1']
        mock_get_zumo_position.return_value = {'xCoord': 0, 'yCoord': 0, 'dx': 10, 'dy': 10}

        result = self.obj_det.handle_object_detection_from_source()
        self.assertIn('zumo', result)
        self.assertIn('objects', result)
        self.mock_camera.release.assert_called_once()


if __name__ == '__main__':
    unittest.main()
