import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from blog_webapp import app, db, bcrypt
from blog_webapp.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm
from blog_webapp.utils import dummy_data
from blog_webapp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


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


def update_user_profile_picture(current_profile_image_file, form_image):
    """
    save profile picture inside static/profile_pictures
    :param current_profile_image_file: name of current profile image
    :param form_image: image input from form
    :return: saved profile picture unique filename
    """

    # delete profile picture if exists
    curr_profile_image_path = os.path.join(app.root_path,
                                           f'static/profile_pics/{current_profile_image_file}')
    if os.path.exists(curr_profile_image_path) \
            and current_profile_image_file != 'default_profile_image.png':
        os.remove(curr_profile_image_path)

    # create unique image file name
    rand_str = secrets.token_hex(8)  # 8 byte hex code
    _, file_ext = os.path.splitext(form_image.filename)  # get the uploaded file extension
    profile_picture_filename = rand_str + file_ext
    profile_picture_path = os.path.join(app.root_path,
                                        f'static/profile_pics',
                                        profile_picture_filename)
    # resize image 125x125
    resize_img_size = (125, 125)
    form_image = Image.open(form_image)
    form_image.thumbnail(resize_img_size)

    # save image
    form_image.save(profile_picture_path)

    return profile_picture_filename


@app.route("/profile", methods=['GET', 'POST'])
@login_required  # don't let user navigate to this page if logged out
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        info_updated = False

        if form.profile_picture.data:
            profile_image_file = update_user_profile_picture(current_user.profile_image_file,
                                                             form.profile_picture.data)
            current_user.profile_image_file = profile_image_file
            info_updated = True

        if form.username.data != current_user.username:
            current_user.username = form.username.data
            info_updated = True

        if form.email.data != current_user.email:
            current_user.email = form.email.data
            info_updated = True

        if info_updated:
            db.session.commit()  # update user in db

        # let user know
        if info_updated:
            flash('Profile updated!', 'success')
        else:
            flash("You didn't update anything.", 'info')

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


@app.route("/post/create", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():

        post = Post(title=form.title.data, content=form.content.data,
                    author=current_user)

        # save the post to database
        db.session.add(post)
        db.session.commit()

        # let the user know
        flash('Your post was uploaded!', 'success')

        # don't let it fall to the return at the end
        # redirect makes a GET request
        # but the last return makes a POST request making a form resubmit
        return redirect(url_for('home'))

    return render_template('create_post.html', title='Create Post', form=form)


@app.route("/post/<int:post_id>")
def get_post(post_id):
    # get_or_404() signals 404 Not Found in the browser automatically if data does not exist
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)
