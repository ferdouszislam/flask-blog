from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

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

# need to import routes after initializing 'app'
# because route also imports 'app' from here
from blog_webapp import routes
