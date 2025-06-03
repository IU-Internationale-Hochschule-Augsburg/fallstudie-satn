import cv2
import itertools
import numpy as np
from src.Classes.FrameProcessor import FrameProcessor



class ObjectDetection:
    def __init__(self):
        self.camera = FrameProcessor()
        self.camera.open()

    def getZumoPosition(self, img, t=175, only_contours=False):
        """
        Detects the position of a Zumo robot based on geometric feature similarity.

        Args:
            img (np.ndarray): Grayscale image.
            t (int): Threshold for binarization.
            only_contours (bool): If True, returns only top contours.

        Returns:
            dict | list: Position info or list of top contours.
        """

        # Invert image colors to highlight bright areas (assuming dark background)
        #inverted = cv2.bitwise_not(img)

        # ERROR: The variable 'blurred' is not defined, this should probably be 'inverted'
        _, thresh = cv2.threshold(img, t, 255, cv2.THRESH_BINARY)

        # Find external contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours by area (descending), pick the top 5 largest ones
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        top_contours = sorted_contours[:5]

        if only_contours:
            return top_contours

        # Try to find the most similar pair of contours to detect Zumo's markers
        best_pair = None
        best_score = 0.0

        for rect1, rect2 in itertools.combinations(top_contours, 2):
            # Extract features from both contours
            area1, aspect1, x1, y1, w1, h1 = self.identify_features(rect1).values()
            area2, aspect2, x2, y2, w2, h2 = self.identify_features(rect2).values()

            # Compute geometric differences
            area_diff = abs(area1 - area2) / max(area1, area2)
            ratio_diff = abs(aspect1 - aspect2) / max(aspect1, aspect2)
            y_diff = abs(y1 - y2)
            x_diff = abs(x1 - x2)

            # Compute a score: smaller is better
            score = (
                    area_diff * 3 +
                    ratio_diff * 2 +
                    y_diff * 0.1 -
                    x_diff * 2
            )

            if score < best_score:
                best_pair = (rect1, rect2)
                best_score = score

        # If a pair was found, return bounding box around both
        x1, y1, w1, h1 = cv2.boundingRect(best_pair[0])
        x2, y2, w2, h2 = cv2.boundingRect(best_pair[1])

        return {
            'xCoord': x1,
            'yCoord': y1,
            'dx': (x2 + w2) - x1,
            'dy': h1
        }

    def get_object_position(self, img, t=115, min_area=500, only_contours=False):
        """
        Detects all objects in the image that are not part of the Zumo robot.

        Args:
            img (np.ndarray): Grayscale image.
            t (int): Threshold for binarization.
            min_area (int): Minimum area for an object to be considered.
            only_contours (bool): If True, return filtered contours.

        Returns:
            list: Object position dictionaries or contours.
        """
        # Get Zumo position to exclude it from object detection
        zumo_data = self.getZumoPosition(img)
        _, tresh = cv2.threshold(img, t, 255, cv2.THRESH_BINARY_INV)

        # Detect contours
        contours, _ = cv2.findContours(tresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by minimum area
        filterd_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
        zumo_x, zumo_y, zumo_w, zumo_h = zumo_data.values()

        if only_contours:
            return filterd_contours

        objects = []

        for cnt in filterd_contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Exclude objects too close to Zumo robot's position
            if abs(x - zumo_x) < w and abs(y - zumo_y) < h:
                continue

            # Add object bounding box
            objects.append({
                'xCoord': x,
                'yCoord': y,
                'dx': w,
                'dy': h
            })

        return objects

    def crop_image(self, gray_img, dark_thresh=118):
        """
        Crops the main region of interest (ROI) based on dark borders and edge detection.

        Args:
            gray_img (np.ndarray): Grayscale image.
            dark_thresh (int): Pixel value considered 'dark' (border).

        Returns:
            np.ndarray: Cropped image region.
        """
        if gray_img is None or gray_img.ndim != 2:
            raise ValueError("Please provide a valid 2D grayscale image.")

        h, w = gray_img.shape

        # Step 1: Detect dark frame mask
        mask_dark = gray_img < dark_thresh
        ys, xs = np.where(mask_dark)

        if len(xs) == 0:
            # No dark frame detected, crop whole image
            x0, y0, x1, y1 = 0, 0, w - 1, h - 1
        else:
            # Calculate bounding box of dark areas
            xmin, xmax = xs.min(), xs.max()
            ymin, ymax = ys.min(), ys.max()
            x0, y0 = max(0, xmin + 1), max(0, ymin + 1)
            x1, y1 = min(w - 1, xmax - 1), min(h - 1, ymax - 1)

        # Step 2: Extract ROI and find edges
        roi = gray_img[y0:y1 + 1, x0:x1 + 1]
        edges = cv2.Canny(roi, 50, 150)
        cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Step 3: Find largest rectangle from contours
        max_area = 0
        best_rect = None
        for cnt in cnts:
            x, y, cw, ch = cv2.boundingRect(cnt)
            area = cw * ch
            if area > max_area:
                max_area = area
                best_rect = (x, y, cw, ch)

        if best_rect is None:
            # No object found, return original ROI
            return roi

        # Step 4: Map cropped box back to original coordinates
        bx, by, bw, bh = best_rect
        abs_x, abs_y = bx + x0, by + y0
        cropped = gray_img[abs_y:abs_y + bh, abs_x:abs_x + bw]

        return cropped

    def identify_features(self, contour):
        """
        Extracts basic shape features from a contour.

        Args:
            contour (np.ndarray): A contour from OpenCV.

        Returns:
            dict: Contains area, aspect ratio, coordinates, width, and height.
        """
        x_coord, y_coord, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = h / w if w != 0 else 0

        return {
            'area': float(area),
            'aspect_ratio': float(aspect_ratio),
            'x_coord': x_coord,
            'y_coord': y_coord,
            'width': w,
            'height': h
        }

    def handle_object_detection_from_source(self):
        print("handle object detection from source")
        ok, gray_frame = self.camera.get_frame()  # get_frame gibt JPEG-Bytes zurück
        print("is_ok", ok)
        print("gray_frame", gray_frame)

        if not ok or gray_frame is None:
            print("poll img")
            while not ok:
                ok, gray_frame = camera.get_frame()
            print("poll finished")

        cropped = self.crop_image(gray_img)
        print(cropped.shape)
        obj_pos = self.get_object_position(cropped)
        zumo_pos = self.get_zumo_position(cropped)
        print(obj_pos)
        print(zumo_pos)

        return {
            'zumo': zumo_pos,
            'objects': obj_pos
        }


