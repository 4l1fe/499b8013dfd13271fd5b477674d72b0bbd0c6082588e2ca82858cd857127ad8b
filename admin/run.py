import flask
import requests
from datetime import datetime, timedelta
from flask.globals import request
from flask import Response, make_response
from db import save, save_img
from config import *


app = flask.Flask(__name__)
data_gen_url = f'http://{DATA_GEN_HOST}:{DATA_GEN_PORT}/generate'
# img_gen_url = 'http://127.0.0.1:8082/generate'


@app.route('/show', methods=['GET'])
def show(): pass


@app.route('/new', methods=['POST'])
def new():
    params = request.get_json()
    # save(params)

    now = datetime.now()
    stop = now.isoformat()
    start = (now - timedelta(days=int(params['interval']))).isoformat()
    resp = requests.post(data_gen_url, json={'function': params['function'], 'start': start, 'stop': stop, 'step': params['step']})
    data = resp.json()

    # resp = requests.post(img_gen_url, json=data})
    # img = resp.data()
    # save_img(img)
    return make_response(str(data))


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
