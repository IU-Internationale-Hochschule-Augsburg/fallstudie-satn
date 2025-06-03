import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from src.Classes.ObjectDetection.ObjectDetection import ObjectDetection  # dein Dateiname hier

class TestObjectDetection(unittest.TestCase):

    def setUp(self):
        self.detector = ObjectDetection()
        self.dummy_img = np.ones((100, 100), dtype=np.uint8) * 255  # weißes Bild

    def test_crop_image_valid_gray(self):
        gray_img = np.zeros((100, 100), dtype=np.uint8)
        cropped = self.detector.crop_image(gray_img)
        self.assertIsInstance(cropped, np.ndarray)
        self.assertEqual(cropped.ndim, 2)

    def test_crop_image_invalid_input(self):
        with self.assertRaises(ValueError):
            self.detector.crop_image(np.zeros((100, 100, 3), dtype=np.uint8))

    def test_identify_features(self):
        contour = np.array([[[10, 10]], [[10, 20]], [[20, 20]], [[20, 10]]])
        result = self.detector.identify_features(contour)
        self.assertIn("area", result)
        self.assertIn("aspect_ratio", result)
        self.assertEqual(result["area"], 121.0)

    @patch('cv2.findContours')
    @patch('cv2.threshold')
    def test_getZumoPosition_only_contours(self, mock_thresh, mock_findContours):
        mock_thresh.return_value = (None, self.dummy_img)
        dummy_contour = np.array([[[0, 0]], [[0, 10]], [[10, 10]], [[10, 0]]])
        mock_findContours.return_value = ([dummy_contour] * 5, None)

        with patch.object(self.detector, 'identify_features') as mock_idf:
            mock_idf.return_value = {
                'area': 100.0,
                'aspect_ratio': 1.0,
                'x_coord': 0,
                'y_coord': 0,
                'width': 10,
                'height': 10
            }

            result = self.detector.get_zumo_position(self.dummy_img, only_contours=True)
            self.assertEqual(len(result), 5)

    @patch('cv2.findContours')
    @patch('cv2.threshold')
    def test_getZumoPosition_full_return(self, mock_thresh, mock_findContours):
        mock_thresh.return_value = (None, self.dummy_img)
        dummy_contour = np.array([[[0, 0]], [[0, 10]], [[10, 10]], [[10, 0]]])
        mock_findContours.return_value = ([dummy_contour] * 5, None)

        with patch.object(self.detector, 'identify_features') as mock_idf:
            mock_idf.side_effect = [
                {'area': 100.0, 'aspect_ratio': 1.0, 'x_coord': 0, 'y_coord': 0, 'width': 10, 'height': 10},
                {'area': 90.0, 'aspect_ratio': 1.0, 'x_coord': 5, 'y_coord': 5, 'width': 9, 'height': 10},
            ]

            result = self.detector.get_zumo_position(self.dummy_img)
            self.assertIn('xCoord', result)
            self.assertIn('yCoord', result)
            self.assertIn('dx', result)
            self.assertIn('dy', result)

    @patch.object(ObjectDetection, 'getZumoPosition')
    @patch('cv2.findContours')
    @patch('cv2.threshold')
    def test_get_object_position_with_objects(self, mock_thresh, mock_findContours, mock_zumo):
        mock_zumo.return_value = {
            'xCoord': 10,
            'yCoord': 10,
            'dx': 5,
            'dy': 5
        }

        dummy_contour = np.array([[[20, 20]], [[20, 40]], [[40, 40]], [[40, 20]]])  # außerhalb von Zumo-Bereich
        mock_thresh.return_value = (None, self.dummy_img)
        mock_findContours.return_value = ([dummy_contour], None)

        result = self.detector.get_object_position(self.dummy_img, only_contours=False)
        print(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
        self.assertIn('xCoord', result[0])

    def test_get_object_position_returns_only_contours(self):
        with patch.object(self.detector, 'getZumoPosition', return_value={
            'xCoord': 0, 'yCoord': 0, 'dx': 0, 'dy': 0
        }), patch('cv2.findContours', return_value=([np.array([[[0, 0]], [[0, 30]], [[30, 30]], [[30, 0]]])], None)), \
             patch('cv2.threshold', return_value=(None, self.dummy_img)):
            result = self.detector.get_object_position(self.dummy_img, only_contours=True)
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)

if __name__ == '__main__':
    unittest.main()