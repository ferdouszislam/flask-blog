import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required

from blog_webapp import app, db, bcrypt, mail
from blog_webapp.forms import (RegistrationForm, LoginForm, UpdateProfileForm, PostForm,
                               RequestResetPasswordForm, ResetPasswordForm)
from blog_webapp.models import User, Post
from blog_webapp.utils.onetime_token_util import get_onetime_token, get_data_from_onetime_token
from flask_mail import Message

@app.route('/')
@app.route('/home')
def home():
    # get the pagination page number from query parameter
    curr_page_num = request.args.get('page_num', 1, type=int)
    # pagination and query to get latest post first
    posts_paginated = Post.query.order_by(Post.timestamp.desc()).paginate(page=curr_page_num, per_page=5)

    # get the list of posts according to pagination parameters
    posts = [post for post in posts_paginated.items]
    all_page_nums = [page_num for page_num in posts_paginated.iter_pages(left_edge=1,
                                                                         left_current=1, right_current=2,
                                                                         right_edge=1)]

    return render_template('home.html', posts=posts, curr_page_num=curr_page_num, all_page_nums=all_page_nums)


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

    return render_template('create_or_edit_post.html', title='Create Post',
                           form=form, legend='Create Post')


@app.route("/post/<int:post_id>")
def get_post(post_id):
    # get_or_404() signals 404 Not Found in the browser automatically if data does not exist
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # get_or_404() signals 404 Not Found in the browser automatically if data does not exist
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        info_updated = False

        if form.title.data != post.title:
            post.title = form.title.data
            info_updated = True

        if form.content.data != post.content:
            post.content = form.content.data
            info_updated = True

        if info_updated:
            # update database
            db.session.commit()

        # let user know
        flash('Your post was updated!', 'success')

        # don't let it fall to the return at the end
        # redirect makes a GET request
        # but the last return makes a POST request making a form resubmit
        return redirect(url_for('get_post', post_id=post.id))

    elif request.method == 'GET':
        # GET request means user navigated to this page and did not submit form
        # populate the form with existing data
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_or_edit_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    # get_or_404() signals 404 Not Found in the browser automatically if data does not exist
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    # delete from database
    db.session.delete(post)
    db.session.commit()

    # let user know
    flash('The post was deleted!', 'success')

    return redirect(url_for('home'))


@app.route('/user/<string:username>/posts', methods=['GET'])
def get_user_posts(username):
    curr_page_num = request.args.get('page_num', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts_paginated = Post.query\
        .filter_by(author=user)\
        .order_by(Post.timestamp.desc())\
        .paginate(page=curr_page_num, per_page=5)

    # get the list of posts according to pagination parameters
    posts = [post for post in posts_paginated.items]
    all_page_nums = [page_num for page_num in posts_paginated.iter_pages(left_edge=1,
                                                                         left_current=1, right_current=2,
                                                                         right_edge=1)]

    return render_template('user_posts.html', posts=posts, curr_page_num=curr_page_num, all_page_nums=all_page_nums, user=user)


def send_reset_password_email_to_user(user):
    token = get_onetime_token({'user_id': user.id})
    email_msg = Message('Password Reset Request',
                        sender='noreply@demo.com',
                        recipients=[user.email])
    email_msg.body = f'''To reset your password click on the link below:
{url_for('reset_password', token=token, _external=True)}
    
If you did not make this request please ignore this email. Thank you.
    '''

    # send the email
    mail.send(email_msg)


@app.route("/request_reset_password", methods=['GET', 'POST'])
def request_reset_password():
    # if user is logged in direct to homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # try-catch in case sending email fails
        try:
            send_reset_password_email_to_user(user)
            flash(f'Please check your email ({user.email}) to reset password.', 'info')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f'Failed to send reset password email, please try again.', 'danger')
            print(f'sending password reset email failed: {str(e)}')
            return redirect(url_for('request_reset_password'))

    return render_template('request_reset_password.html', title='Request Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    # if user is logged in direct to homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    # get user_id from the token and check if user exists
    user_id = get_data_from_onetime_token(token, 'user_id')
    user = User.query.get(user_id)
    if not user:
        flash('Token has expired or is invalid', 'warning')
        # invalid token used redirect to request reset password page
        return redirect(url_for('request_reset_password'))

    # token was valid show user password reset form
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # hash the password
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # save the new password to database
        user.password = password
        db.session.commit()

        flash(f'Password reset successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password', form=form)
