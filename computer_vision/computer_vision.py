import cv2
import numpy as np
import sys

# Importiere deine YoloWrapper- und Kamera-Klasse
from yolo_wrapper import YoloWrapper
from camera_module import Camera  # Passe diesen Import auf deine Kamera-Implementierung an


def main(model_path: str = 'yolo11n-obb.pt'):
    """
    Standalone-Script: Liest Frames von der Kamera, führt YOLO-OBB-Detection aus
    und gibt alle erkannten Bounding-Boxes auf der Konsole aus.
    """
    # Kamera initialisieren
    camera = Camera()
    try:
        camera.open()
    except Exception as e:
        print(f"Fehler beim Öffnen der Kamera: {e}", file=sys.stderr)
        sys.exit(1)

    # YOLO-Wrapper initialisieren (automatischer Download des Modells)
    yolo = YoloWrapper(
        model_path=model_path,
        conf=0.3,
        iou=0.45,
        device='cpu'
    )

    print("Starte Erkennung... Drücke Strg+C zum Beenden.")
    try:
        while True:
            ok, jpeg = camera.get_frame()
            if not ok:
                continue

            # JPEG -> OpenCV-Frame
            arr = np.frombuffer(jpeg, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

            # Objekterkennung
            bboxes = yolo.detect(frame)

            # Bounding-Box-Daten ausgeben
            if bboxes:
                for idx, box in enumerate(bboxes, start=1):
                    print(f"Box {idx}: ")
                    print(f"  x_center: {box['x_center']:.2f}")
                    print(f"  y_center: {box['y_center']:.2f}")
                    print(f"  width:    {box['width']:.2f}")
                    print(f"  height:   {box['height']:.2f}")
                    print(f"  angle:    {box['angle']:.4f} rad")
                    print(f"  confidence: {box['confidence']:.2f}")
                    print(f"  class_id:  {box['class_id']}\n")
            else:
                print("Keine Objekte erkannt.")

    except KeyboardInterrupt:
        print("\nBeende Script auf Nutzerwunsch.")
    finally:
        camera.close()


if __name__ == '__main__':
    # Optional: Modellpfad als erstes Kommandozeilen-Argument
    mp = sys.argv[1] if len(sys.argv) > 1 else 'yolo11n-obb.pt'
    main(mp)
