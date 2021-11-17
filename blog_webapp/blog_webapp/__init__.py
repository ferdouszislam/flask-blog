from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# config vars
app = Flask(__name__)
# secret key for security (used in form html templates)
app.config['SECRET_KEY'] = '45ff14277abe5e2feed981b91e21cb5a'
# database url, using sqlite for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogsite.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# need to import routes after initializing 'app'
# because route also imports 'app' from here
from blog_webapp import routes
