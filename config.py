import os
from dotenv import load_dotenv

load_dotenv("data.env")

secret_key = os.urandom(22).hex()
csrf_key = os.urandom(22).hex()

class main(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = f'{secret_key}'
    WTF_CSRF_SECRET_KEY = f'{csrf_key}'
    LOGIN_KEY = os.environ.get("LOGIN_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = ['pdf']
    ALLOWED_EXTENSIONS_KEY = ['txt']
    LANGUAGES = ['en', 'ru']
    
    # ! EMAIL SETTINGS
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

class mainCfg(main):
    pass