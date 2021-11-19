from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from blog_webapp.config import Config

db = SQLAlchemy()  # sql-alchemy database

bcrypt = Bcrypt()  # for hashing passwords

# login managing library vars
login_manager = LoginManager()
login_manager.login_view = 'users.login'  # login page route
login_manager.login_message_category = 'info'  # 'info' is a bootstrap class
login_manager.login_message = 'Please login to view this page'

mail = Mail()  # to send mail


def create_app(config_cls=Config):
    app = Flask(__name__)
    app.config.from_object(Config)  # set the config variables

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # need to register routes in here
    # need to import routes after initializing 'app'
    # because route also imports 'app' from here
    from blog_webapp.main.routes import main
    from blog_webapp.users.routes import users
    from blog_webapp.posts.routes import posts
    from blog_webapp.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)

    return app
