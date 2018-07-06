from random import getrandbits
from subprocess import run
import os

from MASTML import MASTMLDriver
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/ubuntu/server/public'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"

def get_ext(filename):
    return filename.rsplit('.', 1)[1].lower()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'csv_file' not in request.files or 'conf_file' not in request.files:
            flash('Missing a file part')
            return redirect(request.url)
        csv_file  = request.files['csv_file']
        conf_file = request.files['conf_file']
        # if user does not select file, browser also submit an empty part without filename
        if csv_file.filename == '' or conf_file.filename == '':
            flash('A file is not selected')
            return redirect(request.url)

        if not csv_file or not conf_file:
            flash('A file is false')
            return redirect(request.url)

        csv_filename  = secure_filename(csv_file.filename)
        conf_filename = secure_filename(conf_file.filename)
        if get_ext(csv_filename)!='csv' or get_ext(conf_filename)!='conf':
            flash('Bad file extension')
            return redirect(request.url)

        h = f'{getrandbits(128):032x}'
        zip_filename = h + '.zip'
        unique_dir = os.path.join(app.config['UPLOAD_FOLDER'], h)
        os.mkdir(unique_dir)
        csv_file.save(os.path.join(unique_dir, csv_filename))
        conf_file.save(os.path.join(unique_dir, conf_filename))

        return_to = os.getcwd()
        os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], unique_dir)) # TODO: change how this works
        try:
            mastml = MASTMLDriver(configfile=os.path.split(conf_filename)[-1])
            mastml.run_MASTML()
        except Exception as e:
            print("mastml exception:", e)

        run(['zip', '-r', os.path.join(app.config['UPLOAD_FOLDER'], zip_filename), '.'])
        os.chdir(return_to)
        return redirect(url_for('uploaded_file', filename=zip_filename))

    # GET request:
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
