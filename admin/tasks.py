import io
import logging
import requests
import db
from celery import Celery
from config import RABBIT_HOST, RABBIT_PORT, REDIS_HOST, REDIS_PORT, HIGHCHARTS_HOST, HIGHCHARTS_PORT


app = Celery('tasks', broker=f'pyamqp://guest@{RABBIT_HOST}:{RABBIT_PORT}//', backend=f'redis://{REDIS_HOST}:{REDIS_PORT}')
IMG_GEN_URL = f'http://{HIGHCHARTS_HOST}:{HIGHCHARTS_PORT}'


@app.task
def generate_save_image(data):
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
