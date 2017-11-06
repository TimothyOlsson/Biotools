#Sessions
from flask import session

#Forms
from flask import request, redirect

#Basic rendering
from flask import Flask, render_template

#Sets the website as "app"
app = Flask(__name__)

#List of straff
straff_list = []

#Root page. Runs index.html
@app.route('/')
def index():
    author = "Straff uträkning"
    name = "Test"
    return render_template('index.html', author=author, name=name)

#Cat page
@app.route('/cats', methods = ['GET'])
def cats():
    return render_template('index_cats.html')

#Straff
@app.route('/form', methods = ['GET'])
def form():
    return render_template('form.html', straff_list=straff_list)

#Uses the button
@app.route('/poststraff', methods = ['POST'])
def post():
    straff = request.form['straff']
    straff_list.append(straff)
    session['straff'] = straff
    print(straff_list)
    return redirect('/form')

#A way to unregister straff
@app.route('/unregister')
def unregister():

    unreg_string = ''
    # Make sure they've already registered a straff address
    if 'straff' not in session:
        unreg_string = "You haven't submitted a straff!"
    # Make sure it was already in our address list
    elif session['straff'] not in straff_list:
        unreg_string = "That straff isn't on our list"
    else:
        straff = session['straff']
        straff_list.remove(straff)
        del session['straff'] # Make sure to remove it from the session
        unreg_string = 'Removed ' + straff + ' from the list!'
    return render_template('form.html', unreg_string=unreg_string, straff_list=straff_list)


app.secret_key = r'\x0e\xed]\xd8\x9ae\xf2\x90\xd6\xac\x03\xf4\xddM\xcc\xbb\x1f\xd2a,Z\x0eeW'

if __name__ == "__main__":
    app.run()
