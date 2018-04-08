import logging
import traceback
import requests
import db
from celery import Celery
from config import *


app = Celery('tasks', broker=f'pyamqp://{RABBIT_HOST}:{RABBIT_PORT}//', backend=f'redis://{REDIS_HOST}:{REDIS_PORT}')
app.conf.result_expires = RESULT_EXPIRATION
DATA_GEN_URL = f'http://{DATA_GEN_HOST}:{DATA_GEN_PORT}/generate'
IMG_GEN_URL = f'http://{HIGHCHARTS_HOST}:{HIGHCHARTS_PORT}'


@app.task
def generate_save_image(id_, function, interval, step):
    is_file = False
    try:
        resp = requests.post(DATA_GEN_URL, json={'function': function, 'interval': interval, 'step': step})
        data = resp.json()
        # приведение к милисекундам highcharts
        for item in data:
            item[0] = int(item[0]) * 1000
        params = {'infile':
            {'xAxis': {
                'type': 'datetime'},
                'series': [{
                    'data': data,
                    'type': 'area',}]
            }
        }
        logging.debug(params)
        resp = requests.post(IMG_GEN_URL, json=params)
        if resp.status_code != 200:
            field = '{} {} {}'.format(resp.status_code, resp.reason, resp.text)
        else:
            field = resp.content
            is_file = True
    except Exception:
        field = traceback.format_exc()

    if is_file:
        db.update(id_, image=field)
    else:
        db.update(id_, error=field)
