from flask import Flask, Response
from flask import render_template
import json

from src.Classes.frame_processor import FrameProcessor

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
        'vector':{
            'dx': 10,
            'dy':15
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

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, threaded=True)