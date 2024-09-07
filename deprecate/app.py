# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from werkzeug.utils import secure_filename
from food_recognizer import FoodRecognizer
from secret_key import KIMI_API_KEY

app = Flask(__name__)
CORS(app)  # 启用CORS以允许前端跨域请求

# 配置日志
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, 'app.log')

handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
handler.suffix = "%Y-%m-%d"
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# 初始化 TinyDB
db = TinyDB('foods_db.json')
foods_table = db.table('foods')
users_table = db.table('users')

# 添加上传文件夹配置
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 初始化 FoodRecognizer
food_recognizer = FoodRecognizer(KIMI_API_KEY, app.logger)

def calculate_expiration_date(production_date, shelf_life):
    prod_date = datetime.strptime(production_date, "%Y-%m-%d")
    return (prod_date + timedelta(days=shelf_life)).strftime("%Y-%m-%d")

def calculate_days_left(expiration_date):
    today = datetime.now().date()
    exp_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
    return (exp_date - today).days

@app.route('/api/foods', methods=['GET'])
def get_foods():
    app.logger.info("Received GET request for /api/foods")
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    Food = Query()
    foods = foods_table.search(Food.user_id == int(user_id))
    for food in foods:
        food['daysLeft'] = calculate_days_left(food['expirationDate'])
    sorted_foods = sorted(foods, key=lambda x: x['daysLeft'])
    app.logger.info(f"Returning {len(sorted_foods)} foods for user {user_id}")
    return jsonify(sorted_foods)

@app.route('/api/foods', methods=['POST'])
def add_food():
    app.logger.info("Received POST request for /api/foods")
    
    if request.is_json:
        new_food = request.json
        app.logger.info(f"Received JSON data: {new_food}")
    else:
        new_food = {
            'name': request.form.get('name'),
            'productionDate': request.form.get('productionDate'),
            'shelfLife': request.form.get('shelfLife'),
            'user_id': request.form.get('user_id')
        }
        app.logger.info(f"Received form data: {new_food}")
    
    if 'user_id' not in new_food:
        return jsonify({"error": "User ID is required"}), 400
    
    new_food['shelfLife'] = int(new_food['shelfLife'])
    new_food['user_id'] = int(new_food['user_id'])
    
    new_food['expirationDate'] = calculate_expiration_date(
        new_food['productionDate'], 
        new_food['shelfLife']
    )
    new_food['daysLeft'] = calculate_days_left(new_food['expirationDate'])
    
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            new_food['imagePath'] = file_path
    
    food_id = foods_table.insert(new_food)
    new_food['id'] = food_id
    
    app.logger.info(f"Added new food: {new_food}")
    return jsonify(new_food), 201

@app.route('/api/foods/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    app.logger.info(f"Received DELETE request for /api/foods/{food_id}")
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    Food = Query()
    result = foods_table.remove((Food.id == food_id) & (Food.user_id == int(user_id)))
    if result:
        app.logger.info(f"Deleted food with id: {food_id} for user {user_id}")
        return '', 204
    else:
        app.logger.warning(f"Food with id {food_id} not found for deletion for user {user_id}")
        return jsonify({"error": "Food not found"}), 404

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    User = Query()
    if users_table.search(User.username == username):
        return jsonify({"error": "Username already exists"}), 400
    
    user_id = users_table.insert({
        'username': username,
        'password': password
    })
    
    return jsonify({"id": user_id, "username": username}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    User = Query()
    user = users_table.get(User.username == username)
    
    if user and user['password'] == password:
        return jsonify({"id": user.doc_id, "username": user['username']}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.json
    user_id = data.get('userId')
    new_password = data.get('newPassword')
    
    if not user_id or not new_password:
        return jsonify({"error": "User ID and new password are required"}), 400
    
    User = Query()
    user = users_table.get(doc_id=user_id)
    
    if user:
        users_table.update({'password': new_password}, doc_ids=[user_id])
        return jsonify({"message": "Password changed successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/api/add-secret-key', methods=['POST'])
def add_secret_key():
    data = request.json
    user_id = data.get('userId')
    provider = data.get('provider')
    secret_key = data.get('secretKey')
    
    if not user_id or not provider or not secret_key:
        return jsonify({"error": "User ID, provider, and secret key are required"}), 400
    
    User = Query()
    user = users_table.get(doc_id=int(user_id))
    
    if user:
        users_table.update({'secret_key': secret_key, 'secret_key_provider': provider}, doc_ids=[int(user_id)])
        return jsonify({"message": "Secret key added successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

# Update the food recognition route to use the user's secret key if available
@app.route('/api/recognize-food', methods=['POST'])
def recognize_food():
    print(1)
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
    print(2)
    file = request.files['image']
    user_id = request.form.get('user_id')
    print()
    print(3)
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    print(4)
    if file and user_id:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # try:
        User = Query()
        user = users_table.get(doc_id=int(user_id))
        if not user:
            return jsonify({"error": "Invalid user ID"}), 400
        api_key = user.get('secret_key') if user else KIMI_API_KEY
        
        # Use the user's secret key if available, otherwise use the default
        food_recognizer = FoodRecognizer(api_key, app.logger)
        food_info = food_recognizer.recognize_with_kimi(file_path)
        
        # Delete temporary file
        os.remove(file_path)
        app.logger.info(f"Recognition result: {food_info}")
        return jsonify(food_info)
    
        # except Exception as e:
        #     app.logger.error(f"Error in food recognition: {str(e)}")
        #     return jsonify({"error": "Food recognition failed"}), 500
    else:
        return jsonify({"error": "No selected file"}), 400
if __name__ == '__main__':
    app.run(debug=True)