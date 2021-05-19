from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import mysql
from flask_socketio import SocketIO, send
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

db = SQLAlchemy()
DB_NAME = "social_media"
csrf = CSRFProtect()
mail = Mail()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    csrf.init_app(app)
    app.config['SECRET_KEY'] = 'regegdfgdsvd vdfbgdgdf'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:root@127.0.0.1/{DB_NAME}'
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'christian.petrov999' #os.environ.get('EMAIL_USER') 
    app.config['MAIL_PASSWORD'] = 'qweqweqweA1'  #os.environ.get('EMAIL_PASS')
    mail.init_app(app)
    db.init_app(app)
    socketio.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Post

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('social/' + DB_NAME):
        db.create_all(app=app)
        print('DB created.')

    return app