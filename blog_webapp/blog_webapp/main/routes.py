from flask import Blueprint
from flask import render_template, request, Blueprint
from blog_webapp.models import Post

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
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


@main.route('/about')
def about():
    return render_template('about.html', webpage_title='About')
