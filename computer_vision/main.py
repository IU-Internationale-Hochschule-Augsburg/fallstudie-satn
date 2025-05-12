from flask import *
import json
from src.Classes.frame_processor import *
from src.Classes.TaskPipeline.TaskPipeline import *
from src.Classes.TaskPipeline.TaskForward import *
from src.Classes.TaskPipeline.TaskTurn import *

app = Flask(__name__)
camera = FrameProcessor()


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
    """Direkte MJPEG-Ausgabe aus der Kamera."""
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
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
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
        if duration is None:
            task = TaskForward()
        else:
            task = TaskForward(duration=duration)

    elif task_type == 'turn':
        angle = request_body.get('angle')
        if angle is None:
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
        return Response(status=500)
    return Response(status=200, response =vars(task))

@app.route('/manualControl', methods=['GET'])
def manual_control():
    return render_template('manual_control.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
