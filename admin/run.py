import io
import logging
import db
import tasks
from flask.globals import request
from flask import render_template, send_file, url_for, redirect, Flask
from config import HOST, PORT


app = Flask(__name__)
ALL_ID = 0


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
def generate_image(): # TODO: dont make a task if such id is processed
    id_list = request.form.getlist('id', type=int)
    if ALL_ID in id_list:
        id_list = None

    models = db.get_all(id_list=id_list)
    for model in models:
        tasks.generate_save_image.delay(model['id'], model['function'], model['interval'], model['step'])
    return redirect(url_for('main_page'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host=HOST, port=PORT)
