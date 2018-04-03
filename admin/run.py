import io
import traceback
import logging
import flask
import requests
import db
import tasks
from flask.globals import request
from flask import make_response
from config import HOST, PORT


app = flask.Flask(__name__)


def _show():
    return make_response('ok')


@app.route('/show', methods=['GET'])
def show():
    return _show()

# TODO:  psycopg2 -> psycopg2-binary
@app.route('/new', methods=['POST'])
def new():
    params = request.get_json()
    id_ = db.insert(params['function'], params['interval'], params['step'])
    logging.info("id: %s", id_)
    return _show()


@app.route('/img-gen/register', methods=['POST'])
def register_generation():
    params = request.get_json()
    tasks.generate_save_image.delay(id_, data)
    return _show()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host=HOST, port=PORT)
