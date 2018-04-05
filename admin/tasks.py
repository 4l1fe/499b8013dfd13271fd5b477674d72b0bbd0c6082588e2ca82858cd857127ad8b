import io
import logging
import requests
import db
from celery import Celery
from config import *


app = Celery('tasks', broker=f'pyamqp://{RABBIT_HOST}:{RABBIT_PORT}//', backend=f'redis://{REDIS_HOST}:{REDIS_PORT}')
DATA_GEN_URL = f'http://{DATA_GEN_HOST}:{DATA_GEN_PORT}/generate'
IMG_GEN_URL = f'http://{HIGHCHARTS_HOST}:{HIGHCHARTS_PORT}'


@app.task
def generate_save_image(id_, data):
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
        resp = requests.post(DATA_GEN_URL, json={'function': params['function'], 'interval': params['interval'], 'step': params['step']})
        data = resp.json()
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
    else:
        db.update(id_, error=field)
    # TODO: clean results
