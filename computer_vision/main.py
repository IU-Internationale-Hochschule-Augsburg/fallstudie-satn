from flask import Flask, Response
from flask import render_template
import json

import cv2
import numpy as np  # <-- das

from src.Classes.frame_processor import FrameProcessor
from src.Classes.yolo import YoloWrapper

app = Flask(__name__)
camera = FrameProcessor()
yolo = YoloWrapper('yolo11n-obb.pt', conf=0.3, iou=0.45, device='cpu')

@app.route('/info')
def info():
    return json.dumps({'status': 'running'})

@app.route('/data')
def data():
    coordinat_data = {
        'coords': {
            'coord_x': 10,
            'coord_y': 15
        },
        'vector':{
            'dx': 10,
            'dy':15
        }
    }
    return json.dumps(coordinat_data)

@app.route('/videoCapture')
def video_capture():
    """Direkte MJPEG-Ausgabe aus der Kamera mit YOLO-OBB-Overlay."""
    try:
        camera.open()
    except RuntimeError as e:
        app.logger.error(f"Kamera konnte nicht geöffnet werden: {e}")
        return str(e), 500

    def generate():
        while True:
            try:
                ok, jpeg = camera.get_frame()
                if not ok:
                    continue

                # 1) JPEG-Daten in numpy-Array zurückwandeln
                np_arr = np.frombuffer(jpeg, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                # 2) Objekterkennung + Bounding-Box-Zeichnen
                bboxes = yolo.detect(frame)
                annotated = yolo.draw_boxes(frame, bboxes)

                # 3) Annotiertes Bild wieder zu JPEG komprimieren
                ret, buffer = cv2.imencode('.jpg', annotated)
                if not ret:
                    continue
                jpg_bytes = buffer.tobytes()

                # 4) Yield im MJPEG-Format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n')
            except Exception as e:
                app.logger.error(f"Fehler beim Streamen: {e}")
                break

    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
    
@app.route('/liveStream')
def liveStream():
    return render_template('liveStream.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, threaded=True)