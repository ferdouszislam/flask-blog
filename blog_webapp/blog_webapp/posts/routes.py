from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required

from blog_webapp import db
from blog_webapp.posts.forms import PostForm
from blog_webapp.models import Post


posts = Blueprint('posts', __name__)


@posts.route("/post/create", methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))

    return render_template('create_or_edit_post.html', title='Create Post',
                           form=form, legend='Create Post')


@posts.route("/post/<int:post_id>")
def get_post(post_id):
    # get_or_404() signals 404 Not Found in the browser automatically if data does not exist
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('posts.get_post', post_id=post.id))

    elif request.method == 'GET':
        # GET request means user navigated to this page and did not submit form
        # populate the form with existing data
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_or_edit_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
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

    return redirect(url_for('main.home'))
