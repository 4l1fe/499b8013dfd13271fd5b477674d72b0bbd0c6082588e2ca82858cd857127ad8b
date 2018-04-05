import io
import traceback
import logging
import flask
import requests
import db
import tasks
from flask.globals import request
from flask import render_template, send_file, url_for
from config import HOST, PORT


app = flask.Flask(__name__)


def _main_page():
    models = db.get_all()
    for model in models:
        if model['has_image']:
            model['url'] = url_for('get_image', id_=model['id'])
    add_url = url_for('add_model')
    return render_template('main.html.j2', models=models, add_url=add_url)


@app.route('/', methods=['GET'])
def main_page():
    # TODO: remove {% if error %}
    return _main_page()


@app.route('/image/<int:id_>', methods=['GET'])
def get_image(id_):
    image = db.get_image(id_)
    return send_file(io.BytesIO(image), mimetype='image/png')


# TODO:  psycopg2 -> psycopg2-binary
@app.route('/model', methods=['POST'])
def add_model():
    function = request.form['function']
    interval = int(request.form['interval'])
    step = int(request.form['step'])
    id_ = db.insert(function, interval, step)
    return _main_page()


@app.route('/image', methods=['POST'])
def generate_image  ():
    params = request.get_json()
    tasks.generate_save_image.delay(id_, data)
    return _main_page()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host=HOST, port=PORT)
