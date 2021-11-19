from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from blog_webapp.config import Config


app = Flask(__name__)

# set the config variables
app.config.from_object(Config)

# sql-alchemy database
db = SQLAlchemy(app)

# for hashing passwords
bcrypt = Bcrypt(app)

# manage login
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'  # login page route
login_manager.login_message_category = 'info'  # 'info' is a bootstrap class
login_manager.login_message = 'Please login to view this page'

mail = Mail(app)

# need to register routes in here
# need to import routes after initializing 'app'
# because route also imports 'app' from here
from blog_webapp.main.routes import main
from blog_webapp.users.routes import users
from blog_webapp.posts.routes import posts

app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(posts)
