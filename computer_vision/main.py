from flask import Flask, Response, request
from flask import render_template
import json
from src.Classes.TaskPipeline.TaskForward import *
from src.Classes.TaskPipeline.TaskTurn import *
from src.Classes.TaskPipeline.TaskPipeline import *
from src.Classes.ObjectDetection.ObjectDetection import *
from src.Utils.pathfinding import get_zumo_direction
import cv2

app = Flask(__name__)



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

@app.route('/zumo-position', methods=['GET'])
def zumo_position():
    od = ObjectDetection()
    positions:dict = od.handle_object_detection_from_source()
    zumo_position_data = positions.get("zumo")
    if zumo_position_data is None:
        return Response(status=500)
    zumo_position_data = get_zumo_direction(zumo_position_data)
    return Response(status=200, response=json.dumps(zumo_position_data), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
