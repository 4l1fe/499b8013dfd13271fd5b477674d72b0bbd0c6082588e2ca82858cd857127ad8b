import io
import traceback
import logging
import flask
import requests
import db
import tasks
from datetime import datetime, timedelta
from flask.globals import request
from flask import make_response
from config import DATA_GEN_HOST, DATA_GEN_PORT, HOST, PORT


app = flask.Flask(__name__)
DATA_GEN_URL = f'http://{DATA_GEN_HOST}:{DATA_GEN_PORT}/generate'


@app.route('/show', methods=['GET'])
def show(): pass

#TODO psycopg2 -> psycopg2-binary
@app.route('/new', methods=['POST'])
def new():
    params = request.get_json()
    id_ = db.insert(params['function'], params['interval'], params['step'])
    logging.info("id: %s", id_)

    now = datetime.now()  #TODO move defining, formating to data-gen
    stop = now.isoformat()
    start = (now - timedelta(days=int(params['interval']))).isoformat()
    resp = requests.post(DATA_GEN_URL, json={'function': params['function'], 'start': start, 'stop': stop, 'step': params['step']})
    data = resp.json()

    tasks.generate_save_image.delay(id_, data)
    return make_response('ok')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host=HOST, port=PORT)
