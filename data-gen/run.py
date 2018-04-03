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

    now = datetime.now()  # TODO: move defining, formating to data-gen
    stop = now.isoformat()
    start = (now - timedelta(days=int(params['interval']))).isoformat()

    data = db.generate_data(params['function'], start, stop, params['step'])
    return jsonify(data)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
