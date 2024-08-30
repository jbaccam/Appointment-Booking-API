import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DB_NAME = "database.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DB_NAME = "database.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"
    DEBUG = False
    SQLALCHEMY_ECHO = False
