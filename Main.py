import os #for basic folder handling
from flask import session #Sessions
from flask import request, redirect, url_for #Redirects
from flask import send_from_directory, send_file #Downloading and uploading
from flask import flash #Alerts and flashing
from flask import Flask, render_template #Basic rendering
from werkzeug.utils import secure_filename #Uploading

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

#Root page
@app.route('/')
def index():
    author = "Biohacker"
    options_dict = {'Alignment': ['MSA', 'Alignment', 'cats'],
                   'DNA sequencing': ['Random DNA','DNA translation']}
    
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
    return render_template('/Alignment/MSA.html')

#MSA, text input
@app.route('/MSA', methods=['POST'])
def get_fasta():
    # check if no file and text field is empty. Return and flash an error
    if ('file' not in request.files) and (request.form['fasta_seq'] == ''):
        flash('No file or input detected')
        return redirect(request.url)

    #Prioritize files. Check if file exist
    elif ('file' in request.files):

        #Check if file has no name
        if file.filename == '':
            flash('No filename')
            return redirect(request.url)
        
        #Process file
        file = request.files['file']

        #Check if the file extension is allowed
        if file not allowed_file(file.filename):
            flash('File type not supported')
            return redirect(request.url)

        #If everything is ok
        with open(file,'r') as file_read:
            file_contents = file_read.readlines()
        return(file_contents)

    #If nothing else, use the text field
    else:    
        fasta_seq = request.form['fasta_seq']
        processed_fasta = fasta_seq.upper()
        return processed_fasta

#Alignment page
@app.route('/Alignment')
def Alignment():
    return 'Alignment'

#Cat page
@app.route('/cats', methods = ['GET'])
def cats():
    return render_template('index_cats.html')


app.secret_key = r'\x0e\xed]\xd8\x9ae\xf2\x90\xd6\xac\x03\xf4\xddM\xcc\xbb\x1f\xd2a,Z\x0eeW'

if __name__ == "__main__":
    app.run()







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


