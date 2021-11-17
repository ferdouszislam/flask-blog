from datetime import datetime
from flask import Flask, escape, request, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from utils import dummy_data

# config vars
app = Flask(__name__)
# secret key for security (used in form html templates)
app.config['SECRET_KEY'] = '45ff14277abe5e2feed981b91e21cb5a'
# database url, using sqlite for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogsite.db'
db = SQLAlchemy(app)


# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # string length 20 for hashing image files,
    # so that file names are unique
    profile_image_file = db.Column(db.String(20), nullable=False,
                                   default='default_profile_image.jpg')
    # string length 60 for hashing
    password = db.Column(db.String(60), nullable=False)

    # one user can have many posts
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        # python's toString()
        return f"User('{self.username}', '{self.email}', '{self.profile_image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    # all posts have a user as author
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        # python's toString()
        return f"Post('{self.title}', '{self.timestamp}')"


# apis
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


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@mail.com' and form.password.data == 'pass':
            flash(f'Logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Sorry user does not exist, please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


# this two lines of code lets you run with 'python app.py'
# instead of 'flask run' and setting debug mode True everytime
if __name__ == '__main__':
    app.run(debug=True)
