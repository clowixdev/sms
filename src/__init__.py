from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import main
from flask_babel import Babel
from flask_login import LoginManager, login_manager

app = Flask(__name__, static_folder='static')
app.config.from_object(main)
db = SQLAlchemy(app)
babel = Babel(app)
csrf = CSRFProtect()
csrf.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.init_app(app)

from src.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from src import views