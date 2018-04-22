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

cache = {}

def generate_file_list(ext):
    hrefs = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith("." + ext):
             hrefs.append(url_for('uploaded_file',filename=filename)[1:])
    return hrefs

def allowed_file(filename):
  # this has changed from the original example because the original did not work for me
    return filename[-4:].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def upload_brm_file():
    sel_params = cache.get('selected-params', '')
    if( sel_params =='' ): return redirect(url_for('post_parameters_as_JSON_file'))
    rows,cols = 2,1
    if request.method == 'POST':
        file = request.files['file']
        file_ext = file.filename[-4:].lower()
        if file and file_ext == 'xlsx':
            filename = secure_filename(file.filename)
            print('file uploaded: ' + filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            rf = RulesFactory(app.config['UPLOAD_FOLDER']+'/' + file.filename,rows,cols)
            cache['rf'] = rf
            cache['selected-rule'] = filename
            # for browser, add 'redirect' function on top of 'url_for'
            #href = url_for('uploaded_file',filename=filename)
            rf.show_log = True
            ret = rf.fireBRM()
            rs = rf.collect_rule_statistic(ret)
            return rs
 # Populate html on GET request
    hrefs = generate_file_list('xlsx')

    bttn = ' &nbsp  &nbsp  &nbsp <a href="/?_file='
    hrefs_li = '<ol>' + ''.join(['<li><a href="' + href + '">' + href +'</a>' + bttn + href + '">select</a></li>' for href in hrefs]) + '</ol>'
    
    sel_params = cache.get('selected-params','')
    _file = request.args.get('_file')
    if(_file):
       sel_rules = _file
       cache['selected-rule'] = _file
    else: 
       sel_rules = cache.get('selected-rule','')
    fireBRM =''
    if( sel_rules and sel_params): 
        fireBRM = '<input type="button"  value="FireBRM" onclick="window.location.href=\'fireBRM?selected-params='+ sel_params + '&selected-rule=' +sel_rules+'\'"/>'
        
    print(fireBRM) 
    return '''
    <!doctype html>
    <title>Upload a new BRM rule as Excell spread sheet file</title>
    <h1>Step2: Upload a new BRM rule as Excell spread sheet file</h1>''' + hrefs_li +  '''
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
      <input type=submit value="Upload and Fire BRM">
    <br><br>
    <p>Rules:<b>''' +sel_rules+ ''' </b></p> <p>  Parameters: <b>'''+ sel_params +''' </b></p>
    <br><br>
    ''' + fireBRM +  '''
    </form>
    '''

@app.route('/params', methods=['GET','POST'])
def post_parameters_as_JSON_file():
    if request.method == 'POST':
        file = request.files['file']
        file_ext = file.filename[-4:].lower()
        if file and file_ext == 'json':
            filename = secure_filename(file.filename)
            print('file uploaded: ' + filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename = app.config['UPLOAD_FOLDER']+'/' + file.filename
            file= open(filename,"r+")
            str = file.read()
            cache['selected-params'] = filename
              #Test with JSON array
            RulesFactory.loadParametersFromJSON(str)
            # for browser, add 'redirect' function on top of 'url_for'
            #href = url_for('uploaded_file',filename=filename)
            return redirect(url_for('upload_brm_file'))
  # Populate html on GET request
    hrefs = generate_file_list('json')
    bttn = ' &nbsp  &nbsp  &nbsp <a href="/params?_file='
    hrefs_li = '<ol>' + ''.join(['<li><a href="' + href + '">' + href +'</a>' + bttn + href + '">select</a></li>' for href in hrefs]) + '</ol>'
    
    sel_rules = cache.get('selected-rule','')
    _file = request.args.get('_file')
    if(_file):
        sel_params = _file
        cache['selected-params'] = _file
    else: 
       sel_params = cache.get('selected-params','')
    fireBRM =''
    path_to_select_rules ='/'
    if( sel_rules and sel_params): 
        fireBRM =  '<input type="button"  value="FireBRM" onclick="window.location.href=\'fireBRM?selected-params='+ sel_params + '&selected-rule=' +sel_rules+'\'"/>'
    else: fireBRM = '<input type="button"  value="Next..." onclick="window.location.href=\''+ path_to_select_rules +'\'"/>'
    return '''
    <!doctype html>
    <title>Upload a new BRM rule as Excell spread sheet file</title>
    <h1>Step1: Upload a parmeters as JSON file</h1>''' + hrefs_li +  '''
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
      <input type=submit value="Upload json">
    <br><br> 
    <p>Rules:<b>'''+sel_rules+''' </b></p> <p>  Parameters: <b>'''+ sel_params +''' </b></p>
    <br><br>
    ''' + fireBRM +  '''
    </form>
    '''
@app.route('/fireBRM')
def fireBRM():
    sel_params = request.args.get('selected-params')
    sel_rules = request.args.get('selected-rule')
    rows,cols = 0,1
    if(not sel_rules): sel_rules = cache.get('selected-rule')
    if( sel_params != cache.get('selected-rule')): #refresh cache
           file= open(sel_params,"r+")
           str = file.read()
           cache['selected-params'] = sel_params
                #Prepare params
           rows =  RulesFactory.loadParametersFromJSON(str)
    rf = cache.get('rf')
    if(not rf):
        rf = RulesFactory(sel_rules ,rows,cols)
        ret = rf.fireBRM()
    return rf.collect_rule_statistic(ret)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                                filename)

if (__name__ == '__main__'):
    app.run(debug=True) 

