# http://flask.pocoo.org/docs/patterns/fileuploads/
import os
from flask import Flask, request, redirect, url_for, send_from_directory
from flask import render_template
from werkzeug import secure_filename
from RulesFactory import RulesFactory

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['.txt', '.pdf', 'xlsx', 'json'])
MESSAGE = "<html><head>This BRM engine.</title></head><body><p>BRM engine still running in a test mode.</p></body></html>"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
rf = 0
def allowed_file(filename):
  # this has changed from the original example because the original did not work for me
    return filename[-4:].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def upload_brm_file():
    if(not  RulesFactory.is_params_loaded ) : return redirect(url_for('post_parameters_as_JSON_file'))
    rows,cols = 2,1
    if request.method == 'POST':
        file = request.files['file']
        file_ext = file.filename[-4:].lower()
        if file and file_ext == 'xlsx':
            print ('**found file', file.filename)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            rf = RulesFactory('uploads/' + file.filename,rows,cols)
            # for browser, add 'redirect' function on top of 'url_for'
            href = url_for('uploaded_file',filename=filename)
            ret = rf.fireBRM()
            rs = RulesFactory.collect_rule_statistic(ret)
            return rs
    return '''
    <!doctype html>
    <title>Upload a new BRM rule as Excell spread sheet file</title>
    <h1>Upload a new BRM rule as Excell spread sheet file</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>

    '''

@app.route('/params', methods=['GET','POST'])
def post_parameters_as_JSON_file():
    if request.method == 'POST':
        file = request.files['file']

        file_ext = file.filename[-4:].lower()
        if file and file_ext == 'json':
            str = file.read()
            print(str)
            print ('**found file', file.filename)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
              #Test with JSON array
            RulesFactory.loadParametersFromJSON(str)
            # for browser, add 'redirect' function on top of 'url_for'
            href = url_for('uploaded_file',filename=filename)
            return redirect(url_for('upload_brm_file'))
    return '''
    <!doctype html>
    <title>Upload a new BRM parameters as JSON file</title>
    
    <h1>Upload a new BRM parameters as JSON file</h1>    
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''



@app.route('/fireBRM/')
@app.route('/fireBRM/<name>')
def fireBRM(name=None):
    return rf.fireBRM()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if (__name__ == '__main__'):
   app.run(debug=True) 

