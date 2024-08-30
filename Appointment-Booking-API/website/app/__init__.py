from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .models import User  # Import the User model

    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Import and register blueprints
    from .views.home import home_bp
    from .views.dashboard import dashboard_bp
    from .views.admin import admin_bp
    from .views.manager import manager_bp
    from .auth import auth
    from .appointments import appointments_bp

    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/')
    app.register_blueprint(manager_bp, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(appointments_bp, url_prefix='/')

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    create_database(app)  # Call create_database here

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')
