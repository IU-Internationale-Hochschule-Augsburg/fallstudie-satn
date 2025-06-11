import cv2
import itertools
import numpy as np
from src.Classes.FrameProcessor import FrameProcessor



class ObjectDetection:
    def __init__(self):
        self.camera = FrameProcessor()
        self.camera.open()

    def get_zumo_position(self, img, t=180, only_contours=False):
        """
        Detects the position of a Zumo robot based on geometric feature similarity.

        Args:
            img (np.ndarray): Grayscale image.
            t (int): Threshold for binarization.
            only_contours (bool): If True, returns only top contours.

        Returns:
            dict | list: Position info or list of top contours.
        """


        # ERROR: The variable 'blurred' is not defined, this should probably be 'inverted'
        _, thresh = cv2.threshold(img, t, 255, cv2.THRESH_BINARY_INV)

        # Find external contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area (descending), pick the top 5 largest ones
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        top_contours = sorted_contours[:10]

        if only_contours:
            return top_contours

        # Try to find the most similar pair of contours to detect Zumo's markers
        best_pair = None
        best_score = 999
        print("possible zumo contours", len(top_contours))
        for rect1, rect2 in itertools.combinations(top_contours, 2):
            # Extract features from both contours
            if rect1 is None or rect2 is None:
                return None
            (x1, y1), (w1, h1), angle1 = cv2.minAreaRect(rect1)
            (x2, y2), (w2, h2), angle2 = cv2.minAreaRect(rect2)
            
            fitness_score = 0
            # width health
            if w1 == 0 or w2 == 0:
                fitness_score += 100
            else:
                if (w1 > 100 or w2 > 100) or (w1 < 10 or w2 <10):
                    fitness_score += 100
                else:
                    fitness_score += (h1 / h2) ** 2

            #hight health
            if h1 == 0 or h2 == 0:
                fitness_score += 100
            else:
                if (h1 > 100 or h2 > 100) or (h1 < 10 or h2 <10):
                    fitness_score += 100
                else:
                    fitness_score += (h1 / h2) ** 2
            if (x1 < 10 or x2 < 10) or (x1 > 380 or x2 >380):
                fitness_score += 100
            if (y1 < 10 or y2 < 10) or (y1 > 280 or y2 >280):
                fitness_score += 100
            #angle health
            #fitness_score += (angle1 / angle2) ** 2

            
            if fitness_score < best_score:
                best_pair = (rect1, rect2)
                best_score = fitness_score

        # If a pair was found, return bounding box around both
        if best_pair is None:
            return None
        x1, y1, w1, h1 = cv2.boundingRect(best_pair[0])
        x2, y2, w2, h2 = cv2.boundingRect(best_pair[1])

        return {
            'xCoord': x1,
            'yCoord': y1,
            'dx': (x2 + w2) - x1,
            'dy': h1
        }

    def get_object_position(self, img, t=100, min_area=300, only_contours=False):
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
        zumo_data = self.get_zumo_position(img)
        if zumo_data is None:
            print("No Zumo detected")
            return None
        _, tresh = cv2.threshold(img, t, 190, cv2.THRESH_BINARY_INV)
        print("zumo",zumo_data)
        # Detect contours
        contours, _ = cv2.findContours(tresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if zumo_data is not None:
            zumo_x, zumo_y, zumo_w, zumo_h = zumo_data.values()
        else:
            print("Zumo not found")
            return None
            
        if only_contours:
            return contours

        objects = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Exclude objects too close to Zumo robot's position
            if zumo_data is None or (zumo_data is not None and (abs(x - zumo_x) < (zumo_w * 1.25) and abs(y - zumo_y) < (zumo_h*1.25))):
                continue

            if w * h < min_area:
                continue

            if w < 10 or h < 10:
                continue

            # Add object bounding box
            objects.append({
                'xCoord': x,
                'yCoord': y,
                'dx': w,
                'dy': h
            })
        print("objects", objects)
        return objects

    def crop_image(self, gray_img, dark_thresh=90):
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


        obj_pos = self.get_object_position(gray_frame)
        zumo_pos = self.get_zumo_position(gray_frame)

        print(obj_pos)
        print(zumo_pos)
        self.camera.release()
        return {
            'zumo': zumo_pos,
            'objects': obj_pos
        }


