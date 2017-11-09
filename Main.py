
import os #for basic folder handling
from flask import session #Sessions
from flask import request, redirect, url_for #Redirects
from flask import send_from_directory, send_file #Downloading and uploading
from flask import flash #Alerts and flashing
from flask import Flask, render_template #Basic rendering
from flask import Response #Stream
import threading
import subprocess
import time
from werkzeug.utils import secure_filename #Uploading
import io #String sending
import logging #Debugging
import sys
import multiprocessing

#Sets the website as "app"
app = Flask(__name__)

#Definitions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Uploadiing config
UPLOAD_FOLDER = './uploaded_files'
ALLOWED_EXTENSIONS = set(['txt', 'fasta', 'fa', 'sthlm'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

"""
#Logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='debug.log',
                    level=logging.DEBUG)
"""

#Root page
@app.route('/')
def index():
    author = "Biotools"
    options_dict = {'Alignment': ['MSA', 'Pairwise', 'cats'],
                   'DNA sequencing': ['Random_DNA','Translate_DNA']}

    return render_template('index.html',
                           author=author,
                           alignment_list=options_dict['Alignment'],
                           dnaseq_list=options_dict['DNA sequencing'])

#About page
@app.route('/about')
def about():
    return render_template('about.html')

#MSA page
@app.route('/MSA')
def MSA():
    page = 'MSA'
    folder = 'Alignment'
    if session.get('processed_MSA') != None:
        flag = True
    else:
        flag = False
    return render_template('/'+folder+'/'+page+'.html', processed=flag, page=page)

#MSA, post the fasta
@app.route('/MSA/post', methods=['POST'])
def MSA_get_fasta():
    page = 'MSA'
    folder = 'Alignment'
    if request.form['fasta_seq'] == '':
        flash('No file or input detected')
        return redirect(url_for(page))

    #Prioritize files. Check if file exist
    elif ('file' in request.files) and (request.files['file'].filename != ''):

        file = request.files['file']  #Process file
        session['filename'] = file.filename #add filename to session

        #Check if the file extension is allowed
        if not allowed_file(file.filename):
            flash('File type not supported')
            return redirect(url_for(page))

        file_contents = file.read()  #If everything is ok, read
        #Remove all comments etc
        processed_MSA = file_contents

    #Text field
    else:
        fasta_seq = request.form['fasta_seq']
        processed_MSA = fasta_seq.upper()

    session['processed_MSA'] = processed_MSA

    return redirect(url_for(page))

#MSA, send the fasta
@app.route('/MSA/get', methods=['POST'])
def MSA_send_fasta():
    page = 'MSA'
    folder = 'Alignment'
    """
    Problem fixed. If you use request.form['view'] first while clicking on download,
    the app will crash since it tries to find it in the if statement
    """

    if request.form.get('reset') != None:
        session.clear()
        return redirect(url_for(page))

    elif request.form.get('download') != None:

        bIO = io.BytesIO()
        try:
            bIO.write(session['processed_MSA'].encode('utf-8'))
        except AttributeError:
            bIO.write(session['processed_MSA'])

        bIO.seek(0)

        if session.get('filename') != None:
            filename = 'aligned_' + session['filename']
        else:
            filename = 'aligned_sequences.fasta'

        return send_file(bIO,
                        attachment_filename=filename,
                        as_attachment=True)
    elif request.form.get('view') != None:
        return session['processed_MSA']

#Pairwise page
@app.route('/Pairwise')
def Pairwise():
    page = 'Pairwise'
    folder = 'Alignment'
    if session.get('processed_pairwise') != None:
        flag = True
    else:
        flag = False
    return render_template('/'+folder+'/'+page+'.html', processed=flag, page=page)

#Pairwise, post the fasta
@app.route('/Pairwise/post', methods=['POST'])
def Pairwise_get_fasta():
    page = 'Pairwise'
    folder = 'Alignment'
    if request.form['fasta_seq'] == '':
        flash('No file or input detected')
        return redirect(url_for(page))

    #Prioritize files. Check if file exist
    elif ('file' in request.files) and (request.files['file'].filename != ''):

        file = request.files['file']  #Process file
        session['filename'] = file.filename #add filename to session

        #Check if the file extension is allowed
        if not allowed_file(file.filename):
            flash('File type not supported')
            return redirect(url_for(page))

        file_contents = file.read()  #If everything is ok, read
        processed_pairwise = file_contents

    #Text field
    else:
        fasta_seq = request.form['fasta_seq']
        processed_pairwise = fasta_seq.upper()

    from scripts.NW import Needleman_Wunsch
    parent_pipe, child_pipe = multiprocessing.Pipe()
    process_pairwise = multiprocessing.Process(target=Needleman_Wunsch().run,
                                               args=['AAA', 'AAA', child_pipe])
    process_pairwise.start()

    def wait_for_process():
        pass

    return redirect(url_for(page))

#Pairwise, send the fasta
@app.route('/Pairwise/get', methods=['POST'])
def Pairwise_send_fasta():
    page = 'Pairwise'
    folder = 'Alignment'
    """
    Problem fixed. If you use request.form['view'] first while clicking on download,
    the app will crash since it tries to find it in the if statement
    """

    if request.form.get('reset') != None:
        session.clear()
        return redirect(url_for(page))

    elif request.form.get('download') != None:

        bIO = io.BytesIO()
        try:
            bIO.write(session['processed_MSA'].encode('utf-8'))
        except AttributeError:
            bIO.write(session['processed_MSA'])

        bIO.seek(0)

        if session.get('filename') != None:
            filename = 'aligned_' + session['filename']
        else:
            filename = 'aligned_sequences.fasta'

        return send_file(bIO,
                        attachment_filename=filename,
                        as_attachment=True)
    elif request.form.get('view') != None:
        return session['processed_MSA']

#Random DNA page
@app.route('/Random_DNA')
def Random_DNA():
    return 'Random'

#DNA translation page
@app.route('/Translate_DNA')
def Translate_DNA():
    return 'Translate'

#Cat page
@app.route('/cats', methods = ['GET'])
def cats():
    return render_template('index_cats.html')

app.secret_key = r'\x0e\xed]\xd8\x9ae\xf2\x90\xd6\xac\x03\xf4\xddM\xcc\xbb\x1f\xd2a,Z\x0eeW'

if __name__ == "__main__":
    app.run(threaded=True, debug=True)







"""https://stackoverflow.com/questions/14672753/handling-multiple-requests-in-flask"""

## DUMP

    #return send_file('link.txt', as_attachment=True, mimetype='txt')
"""
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


