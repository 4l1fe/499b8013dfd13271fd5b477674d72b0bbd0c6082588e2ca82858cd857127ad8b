import io
import traceback
import logging
import flask
import requests
import db
from datetime import datetime, timedelta
from flask.globals import request
from flask import Response, make_response, send_file
from config import *


app = flask.Flask(__name__)
DATA_GEN_URL = f'http://{DATA_GEN_HOST}:{DATA_GEN_PORT}/generate'
IMG_GEN_URL = f'http://{HIGHCHARTS_HOST}:{HIGHCHARTS_PORT}'


@app.route('/show', methods=['GET'])
def show(): pass


@app.route('/new', methods=['POST'])
def new():
    params = request.get_json()
    id_ = db.insert(params['function'], params['interval'], params['step'])
    logging.info("id: %s", id_)

    now = datetime.now()  #todo move defining, formating to data-gen
    stop = now.isoformat()
    start = (now - timedelta(days=int(params['interval']))).isoformat()
    resp = requests.post(DATA_GEN_URL, json={'function': params['function'], 'start': start, 'stop': stop, 'step': params['step']})
    data = resp.json()

    chart = {'infile':
                {'xAxis': {
                    'type': 'datetime'},
                'series': [{
                    'type': 'area',
                    'data': data}]
                }
            }

    is_file = False
    try:
        resp = requests.post(IMG_GEN_URL, json=chart)
        logging.info(resp)
        if resp.status_code != 200:
            field = '{} {} {}'.format(resp.status_code, resp.reason, resp.text)
        else:
            field = resp.content
            is_file = True
    except Exception as e:
        field = traceback.format_exc()

    if is_file:
        db.update(id_, image=field)
        return send_file(io.BytesIO(field), mimetype='image/png')

    db.update(id_, error=field)
    return make_response(error)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host=HOST, port=PORT)
