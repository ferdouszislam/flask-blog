from flask import render_template, url_for, flash, redirect
from blog_webapp import app
from blog_webapp.forms import RegistrationForm, LoginForm
from blog_webapp.utils import dummy_data
from blog_webapp.models import User, Post


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
