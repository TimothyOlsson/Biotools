import os  # for basic folder handling
from flask import session  # Sessions
from flask import request, redirect, url_for  # Redirects
from flask import send_from_directory, send_file  # Downloading and uploading
from werkzeug.utils import secure_filename  # Uploading
from flask import flash  # Alerts and flashing
from flask import Flask, render_template  # Basic rendering
from flask.views import View
from flask.views import MethodView
from flask import abort
from flask import jsonify
from flask import Response # Stream
import json
import threading
import subprocess
import time
import io  # String sending
import logging  # Debugging
import sys
import multiprocessing
import random
import string
import binascii

# Sets the website as "app"
app = Flask(__name__)

# CHANGE BEFORE DEPLOYIMENT!
app.secret_key = r'\x0e\xed]\xd8\x9ae\xf2\x90\xd6\xac\x03\xf4\xddM\xcc\xbb\x1f\xd2a,Z\x0eeW'

#region FUNCTIONS
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def key_generator():
    """Returns a random string"""
    return binascii.hexlify(os.urandom(12)).decode()
#endregion

#region CONFIGS
UPLOAD_FOLDER = './uploaded_files'
ALLOWED_EXTENSIONS = set(['txt', 'fasta', 'fa', 'sthlm'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False
#endregion

# Root page
@app.route('/')
def index():
    author = "Biotools"
    """
    New menu = key in dict
    New option = value in dict
    Automatically generated in dropdown menu in index + button that
    sends to correct sub page.
    """
    options_dict = {'Alignment': ['Pairwise', 'MSA', 'cats'],
                   'DNA sequencing': ['Random_DNA','Translate_DNA']}

    return render_template('index.html',
                           author=author,
                           options_dict=options_dict)

# About page
@app.route('/about')
def about():
    return render_template('about.html')

class PairwiseClass(View):
    page = 'Pairwise'  # Page name
    folder = 'Alignment'
    methods = ['POST','GET']

    def __init__(self):
        # Add non-static values here
        pass

    def dispatch_request(self):
        """Dispatches to correct function, property of url_rule"""
        if request.path == '/Pairwise':
            return self.Pairwise()
        elif request.path == '/Pairwise/post':
            return self.Pairwise_post()
        elif request.path == '/Pairwise/get':
            return self.Pairwise_get()
        else:
            abort(404)

    def Pairwise(self):
        submitted = False
        if session.get(self.page+'_key') == None:
            session[self.page+'_key'] = key_generator()
        elif session.get(self.page+'_processing') != None:
            submitted = True
        return render_template('/'+self.folder+'/'+self.page+'.html',
                               submitted=submitted,
                               page=self.page)

    def Pairwise_post(self):
        if request.form['fasta_seq'] == '':
            flash('No file or input detected')
            return redirect(url_for(self.page))
        elif ('file' in request.files) and (request.files['file'].filename != ''):
            file = request.files['file']  #Process file
            session['filename'] = file.filename # add filename to session
            if not allowed_file(file.filename):
                flash('File type not supported')
                return redirect(url_for(self.page))
            file_contents = file.read().decode()  #If everything is ok, read
            from scripts.read_fasta import read_fasta
            names, sequences = read_fasta(file_contents)
        else:
            fasta_seq = request.form['fasta_seq']
            from scripts.read_fasta import read_fasta
            names, sequences = read_fasta(fasta_seq)
        if len(sequences) < 2:
            flash('Only one sequence detected')
            return redirect(url_for(self.page))
        from scripts.Alignment.NW import Needleman_Wunsch
        queue = multiprocessing.Queue()
        align_process = multiprocessing.Process(target=Needleman_Wunsch().run,
                                                args=[sequences[0], sequences[1], queue])
        align_process.start()
        from scripts.sql_handler import sql_handler
        def wait_process(queue, key):
            with app.test_request_context():
                data_dict = queue.get()  # ASYNCHRONOUS fixed :)
                data_dict['KEY'] = key  # Add key for query
                sql_handler().db_add(self.page, data_dict)

        wait_thread = threading.Thread(target=wait_process, args=(queue, session[self.page + '_key'] ))
        wait_thread.start()
        sql_handler().db_clear(self.page, session[self.page + '_key'])  # Clear previous entries
        session[self.page+'_processing'] = 'Working'
        return redirect(url_for(self.page))

    def Pairwise_get(self):
        """
        Problem fixed. If you use request.form['view'] first while clicking on download,
        the app will crash since it tries to find it in the if statement
        """
        if request.form.get('reset') != None:
            session.clear()
            return redirect(url_for(self.page))
        if (request.form.get('download') !=None or request.form.get('view') != None):
            """Check first if calculation is done before doing anything, SQL query fast"""
            from scripts.sql_handler import sql_handler
            if sql_handler().db_find(self.page, session[self.page + '_key']) == None:
                return render_template('loading.html')
        if request.form.get('download') != None:
            bIO = io.BytesIO()
            from scripts.sql_handler import sql_handler
            from scripts.fix_list import fix_list
            bIO.write(fix_list(sql_handler().db_find(self.page,session[self.page+'_key'])).encode())
            bIO.seek(0)
            if session.get('filename') != None:
                filename = 'aligned_' + session['filename']
            else:
                filename = 'aligned_sequences.fasta'
            return send_file(bIO, attachment_filename=filename, as_attachment=True)
        elif request.form.get('view') != None:
            from scripts.sql_handler import sql_handler
            from scripts.fix_list import fix_list
            """<code> makes text monospace, <pre> makes text not ignore multiple spaces
            fix_list fixed the query for output to browser"""
            return '<code>'+'<pre>'+fix_list(sql_handler().db_find(self.page,
                                                                   session[self.page+'_key']),
                                                                   html=True)
#region Pairwise url_rule
app.add_url_rule('/Pairwise', view_func=PairwiseClass.as_view('Pairwise'))
app.add_url_rule('/Pairwise/post', view_func=PairwiseClass.as_view('Pairwise_post'))
app.add_url_rule('/Pairwise/get', view_func=PairwiseClass.as_view('Pairwise_get'))
#endregion

@app.route('/MSA')
def MSA():
    return 'WIP: MSA'

@app.route('/Random_DNA')
def Random_DNA():
    return 'WIP: Random DNA'

@app.route('/Translate_DNA')
def Translate_DNA():
    return 'WIP: Translate DNA'

@app.route('/cats', methods = ['GET'])
def cats():
    return render_template('index_cats.html')


if __name__ == "__main__":
    app.run(threaded=True, debug=True)

#region DUMP
"""
Good links:

https://stackoverflow.com/questions/14672753/handling-multiple-requests-in-flask
https://stackoverflow.com/questions/8179558/how-to-pass-classs-self-through-a-flask-blueprint-route-decorator
http://flask.pocoo.org/docs/0.12/blueprints/
https://www.reddit.com/r/flask/comments/3xk4dq/class_based_views_or_function_based_views/
https://stackoverflow.com/questions/27192932/define-manually-routes-using-flask
https://stackoverflow.com/questions/41051605/refreshing-users-webpage-with-python-flask
"""


"""
How to upload files to server:

#return send_file('link.txt', as_attachment=True, mimetype='txt')
if request.method == 'POST':
# check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    elif not allowed_file(file.filename):
        flash('File type is not supported')        
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('MSA',
                                filename=filename))
"""
#endregion

