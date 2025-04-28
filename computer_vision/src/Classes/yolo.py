from ultralytics import YOLO
import cv2
import numpy as np

class YoloWrapper:
    """
    Wrapper for Ultralytics YOLO models with support for oriented bounding boxes (OBB).
    """

    def __init__(self, model_path: str, conf: float = 0.25, iou: float = 0.45, device: str = 'cpu'):
        """
        Initialize YOLO model.

        :param model_path: Pfad zur .pt- oder .yaml-Datei des YOLO-Modells.
        :param conf: Konfidenzschwelle für NMS (0.0–1.0).
        :param iou: IoU-Schwelle für Non-Maximum Suppression (0.0–1.0).
        :param device: Ausführungsgerät ('cpu' oder 'cuda').
        """
        # Modell laden
        self.model = YOLO(model_path)  # lädt Modell :contentReference[oaicite:1]{index=1}
        # Konfigurationsparameter setzen
        self.model.conf = conf         # NMS-Kofidenzschwelle :contentReference[oaicite:2]{index=2}
        self.model.iou  = iou          # NMS-IoU-Schwelle
        self.model.device = device     # Ausführungsgerät

    def detect(self, frame: np.ndarray) -> list[dict]:
        """
        Führt eine Inferenz auf einem einzelnen Frame aus und gibt alle erkannten
        Bounding-Boxen mit [x_center, y_center, width, height, angle] zurück.

        :param frame: BGR- oder RGB-Frame (np.ndarray).
        :return: Liste von Dictionaries:
                 {'x_center', 'y_center', 'width', 'height', 'angle(radians)',
                  'confidence', 'class_id'}.
        """
        # Inferenz starten (gibt ein Results-Objekt zurück) :contentReference[oaicite:3]{index=3}
        results = self.model.predict(source=frame)[0]
        bboxes = []

        # OBB-Daten: xywhr (x_center, y_center, width, height, rotation in radians) :contentReference[oaicite:4]{index=4}
        if hasattr(results, 'obb') and hasattr(results.obb, 'xywhr'):
            xywhr = results.obb.xywhr.cpu().numpy()
            confs = results.boxes.conf.cpu().numpy()
            cls_ids = results.boxes.cls.cpu().numpy().astype(int)

            for (x, y, w, h, ang), conf, cls in zip(xywhr, confs, cls_ids):
                bboxes.append({
                    'x_center': float(x),
                    'y_center': float(y),
                    'width': float(w),
                    'height': float(h),
                    'angle': float(ang),
                    'confidence': float(conf),
                    'class_id': cls
                })
        else:
            # Fallback auf achsenparallele Boxen
            xyxy = results.boxes.xyxy.cpu().numpy()  # x1,y1,x2,y2
            confs = results.boxes.conf.cpu().numpy()
            cls_ids = results.boxes.cls.cpu().numpy().astype(int)
            for (x1, y1, x2, y2), conf, cls in zip(xyxy, confs, cls_ids):
                w = x2 - x1
                h = y2 - y1
                bboxes.append({
                    'x_center': float(x1 + w/2),
                    'y_center': float(y1 + h/2),
                    'width': float(w),
                    'height': float(h),
                    'angle': 0.0,
                    'confidence': float(conf),
                    'class_id': cls
                })

        return bboxes

    def draw_boxes(self, frame: np.ndarray, bboxes: list[dict]) -> np.ndarray:
        """
        Zeichnet (oriented) bounding boxes in das Bild.

        :param frame: BGR-Frame als numpy array.
        :param bboxes: Liste von Dictionaries aus detect().
        :return: Annotiertes Bild.
        """
        img = frame.copy()
        for box in bboxes:
            # cv2.boxPoints erwartet (center, (w,h), angle_in_degrees) :contentReference[oaicite:5]{index=5}
            rect = (
                (box['x_center'], box['y_center']),
                (box['width'], box['height']),
                box['angle'] * 180 / np.pi  # Radiant → Grad
            )
            pts = cv2.boxPoints(rect).astype(int)
            cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        return img
