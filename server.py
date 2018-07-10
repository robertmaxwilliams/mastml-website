from random import getrandbits
from subprocess import run
import traceback
import os
from os.path import join, splitext, basename

#from MASTML import MASTMLDriver
#from mastml import mastml
from mastml import mastml
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, abort, send_file
import flask
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/Users/max/Repos/mastml-website/public'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"

root = app.config['UPLOAD_FOLDER']
csv_dir = os.path.join(root, 'csv')
conf_dir = os.path.join(root, 'conf')
results_dir = os.path.join(root, 'results')
zip_dir = os.path.join(root, 'zip')

def get_ext(filename):
    return splitext(filename)[1]
    return filename.rsplit('.', 1)[1].lower()

@app.route('/upload', methods=['GET','POST'])
def upload():
    print("UPLOADING AHHHHH")
    print('files:', request.files.getlist("confandcsv"))
    for f in request.files.getlist("confandcsv"):
        filename = secure_filename(f.filename)
        if splitext(basename(filename))[1] == '.csv':
            savepath = csv_dir
        elif splitext(basename(filename))[0] == '.conf':
            savepath = conf_dir
        else:
            flash(f'file {filename} is not a .csv or .conf file, sorry for everything.')
            continue
        f.save(os.path.join(savepath, filename))

    return redirect('/')

@app.route('/run', methods=['POST'])
def run2():
    if 'csv_path' not in request.form or 'conf_path' not in request.form:
        flash('You didnt send me no file names.')
        return redirect('/')
        return redirect(request.url)

    csv_path = request.form['csv_path']
    conf_path = request.form['conf_path']
    do_run(os.path.join(conf_dir, conf_path), os.path.join(csv_dir, csv_path))
    print("running from exising stuff", csv_path, conf_path)
    return redirect('/')

@app.route('/', methods=['GET'])
def index():
    # GET request:
    return render_template('index.html')

# folder directories for results
#@app.route('/results/<path:path>')
#def send_results(path):
#    results_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'results')
#    return send_from_directory(results_dir, path)


@app.route('/results/', defaults={'req_path': 'results'})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    BASE_DIR = app.config['UPLOAD_FOLDER']

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    #files = [os.path.join(os.path.relpath(abs_path, os.path.join(BASE_DIR, 'results')), x) for x in os.listdir(abs_path)]
    files = os.listdir(abs_path)
    url_base = os.path.basename(abs_path) #os.path.relpath(abs_path, BASE_DIR)

    if url_base == 'results':
        url_base = ''

    better_files = [join(url_base, x) for x in files]
    names = [os.path.basename(x) for x in better_files]

    print('\n============ AUGHGHGHGH ================')
    print('BASE_DIR:', BASE_DIR)
    print('abs_path:', abs_path)
    print('files:', files)
    print('url_base:', url_base)
    print('better files:', better_files)
    print('============ ENDENEDNEN ================')

    return render_template('directory.html', zipped_file_and_name=zip(better_files, names))


#@app.route('/results/<path:path>')
#def serve_results(path):
#    # Haven't used the secure way to send files yet
#    return send_from_directory(app.config['UPLOAD_FOLDER']+'/results/', path)

@app.template_global(name='list_confs')
def list_confs():
    return os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'conf'))

@app.template_global(name='list_csvs')
def list_csvs():
    return os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'csv'))

def only_item(ls):
    if len(ls) == 0:
        return ''
    return ls[0]

@app.template_global(name='list_results_and_status')
def list_results_and_status():
    basedir = join(app.config['UPLOAD_FOLDER'], 'results')
    contents = os.listdir(basedir)
    contents = [join(x, only_item(os.listdir(join(basedir, x)))) for x in contents]
    statuses = list()
    for path in contents:
        status = dict()
        status['index'] = os.path.exists(join(results_dir, path, 'index.html'))
        status['errors'] = os.path.exists(join(results_dir, path, 'error.log'))
        status['log'] = os.path.exists(join(results_dir, path, 'log.log'))
        statuses.append(status)

    print(contents)
    return zip(contents, statuses)


app.template_global(name='basename')(os.path.basename)

def mastml_main(conf, csv, savedir, zip_path):
    try:
        print(f'RUNNING MSATML ON {conf_filename} ON {csv_filename} SAVING TO {name}')
        mastml.main(conf, csv, savedir)
    except Exception as e:
        print("mastml exception:", e)
        print(" ========= STACK TRACE =============== ")
        traceback.print_exc()
        print(" ========= ENDDD TRACE =============== ")

    run(['zip', '-r', zip_path, '.'])

def do_run(conf_filename, csv_filename):
    print('doing run: ', conf_filename, csv_filename)

    name = basename(splitext(csv_filename)[0])

    if get_ext(csv_filename)!='.csv' or get_ext(conf_filename)!='.conf':
        flash('Bad file extension')
        print('Bad file extension')
        return redirect(request.url)


    h = f'{getrandbits(128):032x}'
    zip_filename = h + '.zip'
    unique_dir = os.path.join(results_dir, h)
    os.mkdir(unique_dir)
    # mastml does thisbcsv_file.save(os.path.join(unique_dir, csv_filename))
    # mastml does thisbconf_file.save(os.path.join(unique_dir, conf_filename))
    name = os.path.join(unique_dir, name)
    print('doing mastml run in ', name)

    mastml_args = (conf_filename, csv_filename, name, join(zip_dir, zip_filename))
    p = Process(target=mastml_main, args=mastml_args)
    p.start()

    return redirect('/')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
