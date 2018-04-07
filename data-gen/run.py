import flask
import db
from datetime import datetime, timedelta
from flask.globals import request
from flask import jsonify
from config import HOST, PORT


app = flask.Flask('data-gen')


@app.route('/generate', methods=['POST'])
def generate():
    params = request.get_json()
    data = db.generate_data(params['function'], params['interval'], params['step'])
    return jsonify(data)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
