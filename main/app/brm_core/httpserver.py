# http://flask.pocoo.org/docs/patterns/fileuploads/
import os
from flask import Flask, request, redirect, url_for, send_from_directory, session
from flask import render_template
from flask import Markup
from werkzeug import secure_filename

from jinja2 import Environment, PackageLoader, select_autoescape
from time import sleep
import uuid
import logging
from utils.logginginitializer import *



from RulesFactory import RulesFactory


class MainTmplt(object): pass

env = Environment(
    loader=PackageLoader('httpserver','templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['.txt', '.pdf', 'xlsx', 'json'])

MESSAGE = '<head>This BRM engine.</title></head><body><p>BRM engine still running in a test mode.</p></body></html>'
app = Flask(__name__)
app.secret_key = 'any random abrakadabra'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
cache = {}
main_tmplt = MainTmplt()




def generate_file_list(ext):
    hrefs = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith("." + ext):
             hrefs.append(url_for('uploaded_file',filename=filename)[1:])
    return hrefs

def allowed_file(filename):
  # this has changed from the original example because the original did not work for me
    return filename[-4:].lower() in ALLOWED_EXTENSIONS

def prepare_params(filename):
    file_ext = filename[-4:].lower()
    # Prepare parameters
    if(file_ext == 'json'):
        file = open(filename,"r+")
        str  = file.read()
        rows = RulesFactory.load_params_from_json(str)
    else:
        rows = RulesFactory.load_params_from_csv(filename)
    return rows


@app.before_request
def session_management():
    # make the session last indefinitely until it is cleared
    session.permanent = True


@app.route('/ui', methods=['GET','POST'])
def populate_rules_ui():
    template = env.get_template('ui.html')
    return template.render() 

@app.route('/', methods=['GET','POST'])
def upload_brm_file():
    def generate_rules_li():
        hrefs = generate_file_list('xlsx')
        li_markup = Markup('<table>' + ''.join(['<tr>'+
                                    '<td align="left"><a href="/'        + href + '" target="_blank" class="btn btn-primary btn-sm" role="button">View</a></td> ' + 
                                    '<td align="left"><a href="/?_file=' + href + '">' + href[8:] +'</a></td>'+
                                    '</tr>' for href in hrefs]) +
                                    '</table>')
        return li_markup

    # reset the session data
    session.clear()
    #Populate  aka session id 
    if not 'uid' in session :
        session['uid'] = str(uuid.uuid4().node)

    rows,cols = 2,1

    sel_params = cache.get('selected-params', '')

    if request.method == 'POST':
        file = request.files['file']
        file_ext = file.filename[-4:].lower()
        if( file and file_ext == 'xlsx' ):
            filename = secure_filename(file.filename)
            #logger.info('file uploaded: ' + filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename = app.config['UPLOAD_FOLDER'] +'/' + filename

            main_tmplt.hrefs_li = generate_rules_li() 
            main_tmplt.select = 'Select rules'
            if sel_params == '':
                return render_template('main.html',main=main_tmplt)
            #Prepare params (load them from file: sel_params)
            rows = prepare_params(sel_params)

            # load BRM rules
            rf = RulesFactory(filename,rows,1, session.get('uid', None)+ '.log')
            cache['rf'] = rf
            cache['selected-rule'] = filename
            # for browser, add 'redirect' function on top of 'url_for'
            #href = url_for('uploaded_file',filename=filename)
            rf.show_log = True
            ret = rf.fireBRM()
            rs = rf.collect_rule_statistic(ret)
            return rs
 # Populate html on GET request
    if( sel_params =='' ): return redirect(url_for('post_parameters_as_JSON_file'))
    main_tmplt.hrefs_li = generate_rules_li()
    sel_params = cache.get('selected-params','')
    _file = request.args.get('_file')
    if(_file):
       sel_rules = _file
       cache['selected-rule'] = _file
    else: 
       sel_rules = cache.get('selected-rule','')

    main_tmplt.step = "Step 2: Upload a new BRM rule as Excel spread sheet file"
    if( sel_rules and sel_params): 
        main_tmplt.step = "Step 3: Fire BRM rules against parameters or change rules,parameters"
        main_tmplt.fireBRM = Markup('<input type="button" class="btn btn-primary"  value="Fire BRM" onclick="window.location.href=\'fireBRM?selected-params='+ sel_params + '&selected-rule=' +sel_rules+'\'"/>')
    if( sel_params ):
        sel_params_bttn = '<input type="button"  value="select parameters" class="btn btn-primary" onclick="window.location.href=\'params\'"/>'
    main_tmplt.bttns = Markup('''<p><b> Selected Rules: &nbsp;''' +sel_rules+ ''' </b></p>
               <p><b> Selected Parameters:  &nbsp;'''+ sel_params +''' </b> &nbsp''' + sel_params_bttn +'''</p>''')
    main_tmplt.select = 'Select rules'
  #  session['main_tmplt'] = main_tmplt
    return render_template('main.html',main=main_tmplt)
   

@app.route('/params', methods=['GET','POST'])
def post_parameters_as_JSON_file():
    def generate_params_li():
        hrefs = generate_file_list('json')
       # bttn = ' &nbsp  &nbsp  &nbsp <a href="/params?_file='
       # main_tmplt.hrefs_li = Markup('<ol>' + ''.join(['<li><a href="/' + href + '">' + href[8:] +'</a>' + bttn + href + '">>>></a></li>' for href in hrefs]) + '</ol>')
        hrefs_li = Markup('<table>' + ''.join(['<tr>' + 
                                               '<td align="left"> <a href="/' + href + '" target="_blank" class="btn btn-primary btn-sm" role="button">View</a></td>'
                                               '<td align="left"> <a href="/params?_file=' + href + '">' + href[8:] +'</a></td>' +
                                               '</tr>' for href in hrefs]) + '</table>')
        return hrefs_li

    if  not 'uid' in session :
        session['uid'] = str(uuid.uuid4().node)
    if request.method == 'POST':
        file = request.files['file']
        file_ext = file.filename[-4:].lower()
        if (file and (file_ext == 'json' or file_ext == '.csv')):
            filename = secure_filename(file.filename)
            logger.info('file uploaded: ' + filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename = app.config['UPLOAD_FOLDER']+'/' + file.filename
            cache['selected-params'] = filename

            #Prepare params (load them from file)
            rows = prepare_params(filename)

            # for browser, add 'redirect' function on top of 'url_for'
            #href = url_for('uploaded_file',filename=filename)
            return redirect(url_for('upload_brm_file'))
  # Populate html on GET request
  #  main_tmplt = MainTmplt()
    main_tmplt.hrefs_li = generate_params_li()
    
    sel_rules = cache.get('selected-rule','')
    _file = request.args.get('_file')
    if(_file):
        sel_params = _file
        cache['selected-params'] = _file
    else: 
       sel_params = cache.get('selected-params','')

    path_to_select_rules ='/'
    # By default step is 1
    main_tmplt.step = "Step 1: Upload a parmeters as JSON or CSV file"
    if( sel_rules and sel_params):
        main_tmplt.step = "Step 3: Fire BRM rules against parameters or change rules,parameters"
        main_tmplt.fireBRM =  Markup('<input type="button" value="Fire BRM" class="btn btn-primary" onclick="window.location.href=\'fireBRM?selected-params='+ sel_params + '&selected-rule=' +sel_rules+'\'"/>')
    next_bttn=''
    if( sel_params ):
        next_bttn = '<input type="button"  value="select rules" class="btn btn-primary" onclick="window.location.href=\''+ path_to_select_rules +'\'"/>'
    main_tmplt.bttns = Markup('''<p><b> Selected Rules: &nbsp;'''+sel_rules+''' </b> &nbsp''' + next_bttn +'''</p>
                                 <p><b> Selected Parameters: &nbsp; '''+ sel_params +''' </b></p> ''')
    main_tmplt.select = 'Select params'
  #  session['main_tmplt'] = main_tmplt
    return render_template('main.html',main=main_tmplt)


NO_LOG =  "<h3 align='center'>No log file yet</h3>"
def generate(file):
    try:
        with open(file) as f:
                lines = tail(f,1200)
                for line in lines:
                    yield line
    except :
            yield NO_LOG

@app.route('/stream')
def stream():
    if not 'uid' in session :
       session['uid'] = str(uuid.uuid4().node)
       return app.response_class(NO_LOG, mimetype='text/plain')
    else:
       file = output_dir +'/'+ session.get('uid', None) + '.log'
       return app.response_class(generate(file), mimetype='text/plain')

def tail(f, n):
    assert n >= 0
    pos, lines = n+1, []
    while len(lines) <= n:
        try:
            f.seek(-pos, 2)
        except IOError:
            f.seek(0)
            break
        finally:
            lines = list(f)
        pos *= 2
    return lines[-n:]


@app.route('/fireBRM')
def fireBRM():
    sel_params = request.args.get('selected-params')
    sel_rules = request.args.get('selected-rule')
    rows,cols = 0,1
    if(not sel_rules): 
        sel_rules = cache.get('selected-rule')
    if( sel_params != cache.get('selected-rule')): #refresh cache
           cache['selected-params'] = sel_params
           #Prepare params (load them from file)
           rows = prepare_params(sel_params)

    rf = cache.get('rf')
    msg =''
    if(not rf):
        rf = RulesFactory(sel_rules ,rows,cols, session.get('uid', None)+ '.log')
        rf.show_log = True
        ret = rf.fireBRM()
        msg = rf.collect_rule_statistic(ret)
   # main_tmplt = session['main_tmplt']
    main_tmplt.msg = Markup(msg)
    return render_template('main.html',main=main_tmplt)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if (__name__ == '__main__'):
    app.run(host='0.0.0.0',threaded=True,port=8080)


