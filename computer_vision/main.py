from flask import Flask
import json

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
        'vector':{
            'dx': 10,
            'dy':15
        }
    }
    return json.dumps(coordinat_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)