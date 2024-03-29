import datetime
import glob
import hashlib
import os
import re

from flask import Flask
from flask import request, render_template, url_for, redirect, jsonify
from werkzeug.utils import secure_filename

from project2.src.boundaries_creator import BoundariesCreator
from .app import CaSpace

UPLOAD_FOLDER = 'static/temp/'
ALLOWED_EXTENSIONS = {'txt', 'png', 'bmp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists("static"):
    os.mkdir("static")
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def delete_temp():
    folder = "static/temp"
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_file_validity(filename):
    with open('./static/temp/' + str(filename), 'rb') as file:
        lines = file.readlines()
        if 'PNG'.encode('utf-8') in lines[0]:
            with open('./static/temp/temp.txt', 'w') as text:
                for line in lines[3:]:
                    try:
                        decoded = line.decode('utf-8')
                        match = re.search(r'\d\d?\d? \d\d?\d? \d\d?\d?( \d\d?\d?:\d\d?\d?)?\n?', decoded)
                        if match:
                            text.write(match.group())
                    except UnicodeDecodeError:
                        continue
            os.remove('./static/temp/' + str(filename))
            os.rename('./static/temp/temp.txt', './static/temp/' + str(filename))
    with open('./static/temp/' + str(filename), 'r') as file:
        lines = file.readlines()
        init = lines[0].split(' ')
        try:
            if len(lines[1:]) != (int(init[0]) * int(init[1])):
                return False
            if 2 > int(init[2]) or int(init[2]) > max(int(init[0]), int(init[1])) or (int(init[0]) * int(init[1])) < 4:
                return False
            for line in lines[1:]:
                line = line.split(' ')
                if line[3] == line[0] + ':' + line[1]:
                    return False
                if int(line[2]) not in range(int(init[2]) + 1):
                    if int(line[2]) != 999:
                        return False
            return True
        except ValueError:
            return False


@app.route("/", methods=('GET', 'POST'))
def main_page():
    delete_temp()
    if request.method == 'POST':
        try:
            x = int(request.form.get('x'))
            y = int(request.form.get('y'))
            n = int(request.form.get('n'))
            prob = int(request.form.get('prob'))
            inc_n = int(request.form.get('n_inc'))
            inc_type = str(request.form.get('inc_type'))
            inc_r_start = 2 # int(request.form.get('inc_r_start'))
            inc_r_stop = 3 # int(request.form.get('inc_r_stop'))

        except TypeError:
            raise InvalidUsage('Wrong data supplied. Please send valid data via webform.', status_code=400)

        if x not in range(2, 301) or y not in range(2, 301) or n not in range(2, 301) or n > max(x, y):
            raise InvalidUsage('Variables x,y and n must be in range from 2 to 300.'
                               'In addition, n cant be higher than x or y.', status_code=400)

        if inc_n not in range(0, 51):
            raise InvalidUsage('Number of inclusions must be in range from 0 to 50.', status_code=400)

        if inc_r_start not in range(2, 11) or inc_r_stop not in range(2, 11) or inc_r_start > inc_r_stop:
            raise InvalidUsage('Both size start and size stop must be in range from 2 to 10.'
                               'On addition, stop cannot be lower than start', status_code=400)

        if prob not in range(0, 101):
            raise InvalidUsage('Probability should be in range from 0 to 100.', status_code=400)

        CA = CaSpace(x, y, n + 1, prob)
        time = str(datetime.datetime.now()).encode('utf-8')
        name = str(hashlib.sha256(time).hexdigest())

        inc_p = True

        if inc_type == 'Round':
            inc_type = True
        else:
            inc_type = False

        inclusions = [inc_type, inc_n, inc_p, [inc_r_start, inc_r_stop]]

        CA.fill_space(name, inclusions)

        return redirect(url_for('final_page', name=name))

    return render_template('main.html')


@app.route("/import", methods=('GET', 'POST'))
def import_page():
    delete_temp()
    if request.method == 'POST':
        if 'file' not in request.files:
            raise InvalidUsage('Wrong data supplied. Please send data via webform.', status_code=400)
        file = request.files['file']
        if file.filename == '':
            raise InvalidUsage('Wrong data supplied. Please send data via webform.', status_code=400)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            if check_file_validity(filename):
                CA = CaSpace(2, 2, 2)
                CA.import_txt(filename)
                time = str(datetime.datetime.now()).encode('utf-8')
                name = hashlib.sha256(time).hexdigest()
                name = str(name)
                CA.fill_space(name, [0, 0, 0, 0])
                return redirect(url_for('final_page', name=name))
            else:
                raise InvalidUsage('Wrong data supplied. File has been damaged.', status_code=400)

    return render_template('import.html')


@app.route("/final/<name>", methods=('GET', 'POST'))
def final_page(name):
    if len(os.listdir('static/temp')) == 0:
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        try:
            inc_n = int(request.form.get('n_inc'))
            inc_type = str(request.form.get('inc_type'))
            inc_r_start = int(request.form.get('inc_r_start'))
            inc_r_stop = int(request.form.get('inc_r_stop'))
            inc_p = str(request.form.get('inc_p'))
        except TypeError:
            raise InvalidUsage('Wrong data supplied. Please send valid data via webform.', status_code=400)

        CA = CaSpace(2, 2, 2)
        CA.import_txt(name + '.txt')
        time = str(datetime.datetime.now()).encode('utf-8')
        fname = hashlib.sha256(time).hexdigest()
        fname = str(fname)

        if inc_p == 'Random':
            inc_p = True
        else:
            inc_p = False

        if inc_type == 'Round':
            inc_type = True
        else:
            inc_type = False

        inclusions = [inc_type, inc_n, inc_p, [inc_r_start, inc_r_stop]]

        CA.fill_space(fname, inclusions)

        return redirect(url_for('final_page', name=fname))

    return render_template('final.html', name=name)


@app.route("/substractures/<name>", methods=('POST',))
def substracture_endpoint(name):
    if len(os.listdir('static/temp')) == 0:
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        try:
            grain_num = int(request.form.get('grain_n'))
            grain_type = str(request.form.get('grain_type'))

        except TypeError:
            raise InvalidUsage('Wrong data supplied. Please send valid data via webform.', status_code=400)

        CA = CaSpace(2, 2, 2)
        CA.import_txt(name + '.txt')
        time = str(datetime.datetime.now()).encode('utf-8')
        fname = hashlib.sha256(time).hexdigest()
        fname = str(fname)

        CA.fill_space(fname, [0, 0, 0, 0])
        if grain_type == 'Substructure':
            CA.substracture(grain_num, fname)
        elif grain_type == 'Dual Phase':
            CA.dualphase(grain_num, fname)
        else:
            raise InvalidUsage('Wrong data supplied. Please send valid data via webform.', status_code=400)

        return redirect(url_for('final_page', name=fname))

@app.route("/boundaries/<name>", methods=('POST',))
def boundaries_endpoint(name):
    png_file = sorted(glob.glob('static/temp/*.png'))[0]
    bc = BoundariesCreator(png_file)
    bc.decode_image()
    bc.calculate_boundaries()
    bc.create_image()
    time = str(datetime.datetime.now()).encode('utf-8')
    fname = hashlib.sha256(time).hexdigest()
    fname = str(fname)
    return render_template('boundaries.html', name=fname)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    delete_temp()
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
