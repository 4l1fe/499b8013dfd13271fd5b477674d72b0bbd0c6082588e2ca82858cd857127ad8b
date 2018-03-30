import flask
from flask.globals import request
from flask import jsonify
from db import generate_data
from config import *


app = flask.Flask('data-gen')


@app.route('/generate', methods=['POST'])
def generate():
    params = request.get_json()
    data = generate_data(params)
    return jsonify(data)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
