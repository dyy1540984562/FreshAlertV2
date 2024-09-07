import os
from datetime import timedelta
from .secret_key import KIMI_API_KEY
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
    LOG_FOLDER = os.path.join(BASE_DIR, '..', 'logs')
    DB_FILE = os.path.join(BASE_DIR, '..', 'foods_db.json')
    KIMI_API_KEY = os.environ.get('KIMI_API_KEY') or KIMI_API_KEY
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.LOG_FOLDER, exist_ok=True)