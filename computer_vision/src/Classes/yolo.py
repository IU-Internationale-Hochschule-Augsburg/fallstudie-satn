from ultralytics import YOLO
import cv2
import numpy as np
import torch

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
        self.model = YOLO(model_path)

        # Modell auf das gewünschte Gerät verschieben
        if device == 'cuda' and torch.cuda.is_available():
            self.model.to('cuda')
        else:
            self.model.to('cpu')

        # Konfigurationsparameter setzen
        self.model.conf = conf
        self.model.iou = iou
        self.device = device

    def detect(self, frame: np.ndarray) -> list[dict]:
        # Inferenz ausführen
        results = self.model.predict(source=frame, device=self.device, verbose=False)[0]
        bboxes = []

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
            xyxy = results.boxes.xyxy.cpu().numpy()
            confs = results.boxes.conf.cpu().numpy()
            cls_ids = results.boxes.cls.cpu().numpy().astype(int)
            for (x1, y1, x2, y2), conf, cls in zip(xyxy, confs, cls_ids):
                w = x2 - x1
                h = y2 - y1
                bboxes.append({
                    'x_center': float(x1 + w / 2),
                    'y_center': float(y1 + h / 2),
                    'width': float(w),
                    'height': float(h),
                    'angle': 0.0,
                    'confidence': float(conf),
                    'class_id': cls
                })

        return bboxes

    def draw_boxes(self, frame: np.ndarray, bboxes: list[dict]) -> np.ndarray:
        img = frame.copy()
        for box in bboxes:
            rect = (
                (box['x_center'], box['y_center']),
                (box['width'], box['height']),
                box['angle'] * 180 / np.pi
            )
            pts = cv2.boxPoints(rect).astype(int)
            cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        return img
