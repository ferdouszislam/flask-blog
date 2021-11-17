from flask import render_template, url_for, flash, redirect, request
from blog_webapp import app, db, bcrypt
from blog_webapp.forms import RegistrationForm, LoginForm, UpdateProfileForm
from blog_webapp.utils import dummy_data
from blog_webapp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


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
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # hash the password
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # save user info to database
        user = User(username=form.username.data, email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)

            # login_manager hits '/login' route with a parameter of next_page
            # next_page is the route user tried to access without logging in
            # next_page will be None if /login route is hit anything else but the login_manager
            next_page = request.args.get('next', None)

            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash(f'Sorry user does not exist, please check your email and password.', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/profile", methods=['GET', 'POST'])
@login_required  # don't let user navigate to this page if logged out
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        # update user in db
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        # let user know
        flash('Profile updated!', 'success')

        # don't let it fall to the return at the end
        # redirect makes a GET request
        # but the last return makes a POST request making a form resubmit
        return redirect(url_for('profile'))

    elif request.method == 'GET':
        # GET request means user navigated to this page and did not just submit form
        # populate the form with existing user data
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image_file = url_for('static', filename=f'profile_pics/{current_user.profile_image_file}')
    return render_template('profile.html', title='User Profile',
                           profile_image_file=profile_image_file, form=form)
