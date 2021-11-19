import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# config vars
app = Flask(__name__)

# secret key for security (used in form html templates)
app.config['SECRET_KEY'] = '45ff14277abe5e2feed981b91e21cb5a'

# database url, using sqlite for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogsite.db'
# sql-alchemy database
db = SQLAlchemy(app)

# for hashing passwords
bcrypt = Bcrypt(app)

# manage login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # login page route
login_manager.login_message_category = 'info'  # 'info' is a bootstrap class
login_manager.login_message = 'Please login to view this page'

# email config vars
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
mail = Mail(app)
# print(app.config['MAIL_PASSWORD'])

# need to import routes after initializing 'app'
# because route also imports 'app' from here
from blog_webapp import routes
