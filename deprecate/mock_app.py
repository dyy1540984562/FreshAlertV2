from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/foods', methods=['GET'])
def get_foods():
    return jsonify({"error": "Failed to fetch foods"}), 500

@app.route('/api/foods', methods=['POST'])
def add_food():
    return jsonify({"error": "Failed to add food"}), 500

@app.route('/api/foods/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    return jsonify({"error": "Failed to delete food"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    return jsonify({"error": "Registration failed"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    return jsonify({"error": "Login failed"}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 使用不同的端口，以免与原始app冲突