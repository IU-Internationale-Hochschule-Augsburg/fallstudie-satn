import cv2
import itertools
import numpy as np

class ObjectDetection:
    def __init__(self):
        pass

    def getZumoPosition(self, img, t=175):
        inverted = cv2.bitwise_not(img)
        grayTone = cv2.cvtColor(inverted, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(grayTone, (5, 5), 0)

        _, thresh = cv2.threshold(blurred, t, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        top_contours = sorted_contours[:5]

        best_pair = None
        best_score = 0.0

        for rect1, rect2 in itertools.combinations(top_contours, 2):
            area1, aspect1, x1, y1, w1, h1 = self.identify_features(rect1).values()
            area2, aspect2, x2, y2, w2, h2= self.identify_features(rect2).values()
            area_diff = abs(area1 - area2) / max(area1, area2)
            ratio_diff = abs(aspect1 - aspect2) / max(aspect1, aspect2)
            y_diff = abs(y1 - y2)
            x_diff = abs(x1 - x2)

            score = (
                    area_diff * 3 +
                    ratio_diff * 2 +
                    y_diff * 0.1 -
                    x_diff * 2
            )

            if score < best_score:
                best_pair = (rect1, rect2)
                best_score = score
        print(best_pair)
        x1, y1, w1, h1 = cv2.boundingRect(best_pair[0])
        x2, y2, w2, h2 = cv2.boundingRect(best_pair[1])

        return {
                'xCoord':x1,
                'yCoord': y1,
                'dx': (x2 + w2) - x1,
                'dy': h1
            }


    def get_object_position(self, img, t=115, min_area=500, only_contours=False):
        _, tresh = cv2.threshold(img, t, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(tresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        filterd_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

        if only_contours:
            return filterd_contours

        objects = []
        for cnt in filterd_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            objects.append({
                'xCoord':x,
                'yCoord': y,
                'dx': w,
                'dy': h
            })
        return objects


    def crop_image(self, gray_img, dark_thresh=118):
        if gray_img is None or gray_img.ndim != 2:
            raise ValueError("Bitte ein gültiges 2D‑Graustufenbild übergeben.")

        h, w = gray_img.shape

        # 1) Rahmen-Maske
        mask_dark = gray_img < dark_thresh
        ys, xs = np.where(mask_dark)
        if len(xs) == 0:
            # kein Rahmen → gesamte Fläche
            x0, y0, x1, y1 = 0, 0, w - 1, h - 1
        else:
            xmin, xmax = xs.min(), xs.max()
            ymin, ymax = ys.min(), ys.max()
            x0, y0 = max(0, xmin + 1), max(0, ymin + 1)
            x1, y1 = min(w - 1, xmax - 1), min(h - 1, ymax - 1)

        # 2) ROI und Konturen
        roi = gray_img[y0:y1 + 1, x0:x1 + 1]
        edges = cv2.Canny(roi, 50, 150)
        cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 3) größte Box suchen
        max_area = 0
        best_rect = None
        for cnt in cnts:
            x, y, cw, ch = cv2.boundingRect(cnt)
            area = cw * ch
            if area > max_area:
                max_area = area
                best_rect = (x, y, cw, ch)

        if best_rect is None:
            # keine Objekte gefunden → gib ROI zurück
            return roi

        # 4) auf Originalbild umrechnen und zuschneiden
        bx, by, bw, bh = best_rect
        abs_x, abs_y = bx + x0, by + y0
        cropped = gray_img[abs_y:abs_y + bh, abs_x:abs_x + bw]

        return cropped

    def identify_features(self,contour):
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

    def demo_object_detection(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cropped = self.crop_image(gray)
        contours = self.get_object_position(cropped, only_contours=True)

        cv2.drawContours(cropped, contours, -1, (255, 0, 0), 3)
        cv2.imshow("Object Detection", cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()