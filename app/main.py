from flask import Flask
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import Config
from app.api.routes import api

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    Config.init_app(app)  # 确保这行被调用
    
    CORS(app)
    
    app.register_blueprint(api, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)