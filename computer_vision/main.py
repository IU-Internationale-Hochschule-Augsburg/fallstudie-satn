from flask import Flask, Response, request
from flask import render_template
import json
from src.Classes.TaskPipeline.TaskForward import *
from src.Classes.TaskPipeline.TaskTurn import *
from src.Classes.TaskPipeline.TaskPipeline import *
from src.Classes.ObjectDetection.ObjectDetection import *
import cv2

app = Flask(__name__)
camera = FrameProcessor()
camera.open()


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
        'vector': {
            'dx': 10,
            'dy': 15
        }
    }
    return json.dumps(coordinat_data)


@app.route('/videoCapture')
def video_capture():
    """Direkte MJPEG-Ausgabe aus der Kamera (NumPy-Array intern, JPEG erst hier)."""
    try:
        camera.open()
    except RuntimeError as e:
        app.logger.error(f"Kamera konnte nicht geöffnet werden: {e}")
        return str(e), 500

    def generate():
        while True:
            try:
                ok, gray_frame = camera.get_frame()
                if not ok or gray_frame is None:
                    continue
                print(gray_frame.shape)
                # Optional: Konturen in das Frame einzeichnen
                # Wenn ihr obj‐Erkennung direkt auf dem Grauwert-Array durchführen wollt:
                od = ObjectDetection()
                # Beispiel: nur Konturen abfragen (liefert Liste[np.ndarray])
                contours = od.get_object_position(gray_frame, only_contours=True)
                # Um Konturen sichtbar zu machen, müssen wir ein Farb-Bild erzeugen:
                color_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
                cv2.drawContours(color_frame, contours, -1, (0, 255, 0), 2)

                # Jetzt color_frame (BGR uint8) in JPEG kodieren
                success, jpeg_buf = cv2.imencode('.jpg', color_frame)
                if not success:
                    continue
                jpeg_bytes = jpeg_buf.tobytes()
                print(od.handle_object_detection_from_source())
                # MJPEG-Frame senden
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')
            except Exception as e:
                app.logger.error(f"Fehler beim Streamen: {e}")
                break

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/liveStream')
def liveStream():
    return render_template('liveStream.html')


@app.route('/task', methods=['POST'])
def add_task():
    print("received task")
    request_body = request.get_json()
    task_type = request_body.get('type')
    task = None
    if task_type == 'forward':
        duration = request_body.get('duration')
        if duration is None or type(duration) not in [int, float]:
            task = TaskForward()
        else:
            task = TaskForward(duration=duration)

    elif task_type == 'turn':
        angle = request_body.get('angle')
        if angle is None or type(angle) not in [int, float]:
            task = TaskTurn()
        else:
            task = TaskTurn(angle=angle)
    else:
        return Response(status=400, response=f'could not identify task type ${task_type}')
    pipe = TaskPipeline()
    if pipe.push_task(task=task):
        print("added task", vars(task), "to pipeline")
    else:
        print("failed adding task", vars(task), "to pipeline")
        return Response(status=500)

    return Response(status=200)

@app.route('/task', methods=['GET'])
def get_task():
    pipe = TaskPipeline()
    task = pipe.pop_task()
    if task is None:
        return Response(status=404)
    print("returning task:",vars(task))
    return Response(status=200, response=json.dumps(vars(task)), mimetype='application/json')

@app.route('/manualControl', methods=['GET'])
def manual_control():
    return render_template('manual_control.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
