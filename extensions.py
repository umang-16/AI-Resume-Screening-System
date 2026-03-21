# pyre-ignore-all-errors
from flask_sqlalchemy import SQLAlchemy # pyre-ignore
from flask_login import LoginManager # pyre-ignore

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
