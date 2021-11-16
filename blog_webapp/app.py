from flask import Flask, escape, request, render_template
from utils import dummy_data

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=dummy_data.posts)
# def hello():
#     name = request.args.get("name", "World")
#     return f'Hello, {escape(name)}!'


@app.route('/about')
def about():
    return render_template('about.html', webpage_title='About')


# this two lines of code lets you run with 'python app.py'
# instead of 'flask run' and setting debug mode True everytime
if __name__ == '__main__':
    app.run(debug=True)
