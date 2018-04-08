import io
import logging
import db
import tasks
from flask.globals import request
from flask import render_template, send_file, url_for, redirect, Flask
from celery import states
from redis import Redis
from config import HOST, PORT, REDIS_HOST, REDIS_PORT, RESULT_EXPIRATION


app = Flask(__name__)
ALL_ID = 0
NS_ADMIN = 'admin:'
NS_CREATED_TASK = NS_ADMIN + 'created-task:'


@app.route('/', methods=['GET'])
def main_page():
    models = db.get_all()
    for model in models:
        if model['has_image']:
            model['url'] = url_for('get_image', id_=model['id'])
    add_url = url_for('add_model')
    img_gen_url = url_for('generate_image')
    return render_template('main.html.j2', models=models, add_url=add_url, img_gen_url=img_gen_url, ALL_ID=ALL_ID)


@app.route('/image/<int:id_>', methods=['GET'])
def get_image(id_):
    image = db.get_image(id_)
    return send_file(io.BytesIO(image), mimetype='image/png')


@app.route('/model', methods=['POST'])
def add_model():
    function = request.form['function']
    interval = int(request.form['interval'])
    step = int(request.form['step'])
    id_ = db.insert(function, interval, step)
    return redirect(url_for('main_page'))


@app.route('/image', methods=['POST'])
def generate_image():
    id_list = request.form.getlist('id', type=int)
    if ALL_ID in id_list:
        id_list = None

    r = Redis(host=REDIS_HOST, port=REDIS_PORT)
    models = db.get_all(id_list=id_list)
    for model in models:
        task_id = str(model['id'])
        task_state = tasks.app.AsyncResult(task_id).state
        # задача создана и в процессе обработки
        if r.exists(NS_CREATED_TASK+task_id) and task_state not in states.READY_STATES:
            logging.warning(f'task {model["id"]} is processed')
            continue

        tasks.generate_save_image.apply_async(args=(model['id'], model['function'], model['interval'], model['step']),
                                              task_id=task_id)
        r.set(NS_CREATED_TASK+task_id, True, ex=RESULT_EXPIRATION)
    return redirect(url_for('main_page'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host=HOST, port=PORT)
