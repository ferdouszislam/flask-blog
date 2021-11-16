from flask import Flask, escape, request

app = Flask(__name__)


@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'


# this two lines of code lets you run with 'python app.py'
# instead of 'flask run' and setting debug mode True everytime
if __name__ == '__main__':
    app.run(debug=True)
