"""
This imports the Flask library and
creates a new website in a variable called app.
"""
from flask import Flask
app = Flask(__name__)


"""
The @ is new, it’s called a decorator and it is used to ‘augment’ function definitions.
Flask uses route() to say that if the browser requests the address / (the default, or home address),
then our app should route that request to this hello_world function.

The function itself returns the string “Hello World!”. This will be sent to the web browser.
"""
@app.route('/')
def hello_world():
    return 'Hello World!'


"""
This is Python for “if this script is run directly then start the application”.

Now you can start running your first website! In your terminal:
"""
if __name__ == '__main__':
    app.run()

