from datetime import datetime
from blog_webapp import db


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
