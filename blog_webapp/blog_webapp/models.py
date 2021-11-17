from datetime import datetime
from blog_webapp import db, login_manager
from flask_login import UserMixin


# for login manager to fetch user info using user_id from session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# UserMixin is needed for the flask_login library's built-in login authentication
class User(db.Model, UserMixin):
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
