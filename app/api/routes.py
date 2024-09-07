from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
import os
from app.services.food_service import FoodService
from app.services.user_service import UserService
from app.utils.logger import setup_logger
from app.config import Config
# from flask_jwt_extended import jwt_required, get_jwt_identity

api = Blueprint('api', __name__)

def get_food_service():
    if not hasattr(api, 'food_service'):
        config = Config()
        for key, value in current_app.config.items():
            setattr(config, key, value)
        api.food_service = FoodService(config)
    return api.food_service

def get_user_service():
    if not hasattr(api, 'user_service'):
        config = Config()
        for key, value in current_app.config.items():
            setattr(config, key, value)
        api.user_service = UserService(config)
    return api.user_service

def setup_services():
    if not hasattr(api, 'logger'):
        api.logger = setup_logger('api', current_app.config['LOG_FOLDER'])

@api.before_request
def before_request():
    setup_services()

@api.route('/foods', methods=['GET'])
# @jwt_required()
def get_foods():
    # userId = get_jwt_identity()
    user_id = request.args.get('userId')
    if user_id == None:
        return jsonify({"error": "userId not found"}), 400
    foods = get_food_service().get_foods(user_id)
    return jsonify(foods)

@api.route('/foods', methods=['POST'])
# @jwt_required()
def add_food():
    user_id = request.form.get('userId') or request.json.get('user_id')  # 从表单或 JSON 数据获取 user_id
    if request.is_json:
        new_food = request.json
    else:
        new_food = request.form.to_dict()
    
    new_food['user_id'] = user_id
    
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            new_food['imagePath'] = file_path
    
    added_food = get_food_service().add_food(new_food)
    return jsonify(added_food), 201

@api.route('/foods/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    user_id = request.args.get('user_id')  # 从查询参数获取 user_id
    result = get_food_service().delete_food(food_id, user_id)
    if result:
        return '', 204
    return jsonify({"error": "Food not found"}), 404

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    result = get_user_service().register(data['username'], data['password'])
    if result:
        return jsonify(result), 201
    return jsonify({"error": "Username already exists"}), 400

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    user = get_user_service().login(data['username'], data['password'])
    if user:
        return jsonify(user), 200
    return jsonify({"error": "Invalid username or password"}), 401

@api.route('/change-password', methods=['POST'])
def change_password():
    user_id = request.json.get('userId')
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400
    new_password = request.json.get('newPassword')
    if get_user_service().change_password(user_id, new_password):
        return jsonify({"message": "Password changed successfully"}), 200
    return jsonify({"error": "User not found"}), 404

@api.route('/add-secret-key', methods=['POST'])
def add_secret_key():
    user_id = request.json.get('user_id')
    provider = request.json.get('provider')
    secret_key = request.json.get('secretKey')
    if get_user_service().add_secret_key(user_id, provider, secret_key):
        return jsonify({"message": "Secret key added successfully"}), 200
    return jsonify({"error": "User not found"}), 404

@api.route('/recognize-food', methods=['POST'])
def recognize_food():
    user_id = request.form.get('user_id')
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            food_info = get_food_service().recognize_food(file_path, user_id)
            os.remove(file_path)
            return jsonify(food_info)
        except Exception as e:
            api.logger.error(f"Error in food recognition: {str(e)}")
            return jsonify({"error": "Food recognition failed"}), 500
    
    return jsonify({"error": "Invalid file"}), 400