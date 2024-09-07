import pytest
from flask import json
import sys
import os
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import create_app
from app.config import Config

@pytest.fixture
def client():
    app = create_app(Config)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_foods(client):
    response = client.get('/api/foods?userId=1')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    if len(response.json) > 0:
        assert 'name' in response.json[0]

def test_get_foods_without_user_id(client):
    response = client.get('/api/foods')
    assert response.status_code == 400
    assert 'error' in response.json

def test_add_food(client):
    data = {
        "name": "Test Banana",
        "productionDate": "2023-01-01",
        "shelfLife": 5,
        "userId": 1
    }
    
    response = client.post('/api/foods', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    assert response.json['name'] == 'Test Banana'

def test_delete_food(client):
    # 首先添加一个食品
    add_response = client.post('/api/foods', data=json.dumps({
        "name": "Test Apple",
        "productionDate": "2023-01-01",
        "shelfLife": 7,
        "userId": 1
    }), content_type='application/json')
    
    food_id = add_response.json['id']
    
    # 然后删除这个食品
    delete_response = client.delete(f'/api/foods/{food_id}?user_id=1')
    assert delete_response.status_code == 204

def test_register(client):
    data = {
        "username": f"testuser_{os.urandom(4).hex()}",
        "password": "testpassword"
    }
    
    response = client.post('/api/register', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['username'] == data['username']

def test_login(client):
    # 首先注册一个用户
    register_data = {
        "username": f"loginuser_{os.urandom(4).hex()}",
        "password": "testpassword"
    }
    client.post('/api/register', data=json.dumps(register_data), content_type='application/json')
    
    # 然后尝试登录
    login_data = {
        "username": register_data['username'],
        "password": register_data['password']
    }
    
    response = client.post('/api/login', data=json.dumps(login_data), content_type='application/json')
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['username'] == register_data['username']

def test_change_password(client):
    # 首先注册一个用户
    register_data = {
        "username": f"changepassuser_{os.urandom(4).hex()}",
        "password": "oldpassword"
    }
    register_response = client.post('/api/register', data=json.dumps(register_data), content_type='application/json')
    user_id = register_response.json['id']
    
    # 然后更改密码
    change_password_data = {
        "userId": user_id,
        "newPassword": "newpassword"
    }
    
    response = client.post('/api/change-password', data=json.dumps(change_password_data), content_type='application/json')
    assert response.status_code == 200
    assert 'message' in response.json

def test_add_secret_key(client):
    # 首先注册一个用户
    register_data = {
        "username": f"secretkeyuser_{os.urandom(4).hex()}",
        "password": "testpassword"
    }
    register_response = client.post('/api/register', data=json.dumps(register_data), content_type='application/json')
    user_id = register_response.json['id']
    
    # 然后添加密钥
    data = {
        "user_id": user_id,
        "provider": "kimi",
        "secretKey": "test_secret_key"
    }
    
    response = client.post('/api/add-secret-key', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert 'message' in response.json

def test_recognize_food(client):
    # 使用绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_image_path = os.path.join(current_dir, 'test.jpg')
    
    # 检查文件是否存在
    if not os.path.exists(test_image_path):
        pytest.fail(f"Test image not found at {test_image_path}")
    
    try:
        with open(test_image_path, 'rb') as img_file:
            data = {
                'user_id': '1',
                'image': (img_file, 'test.jpg')
            }
            response = client.post('/api/recognize-food', 
                                   data=data, 
                                   content_type='multipart/form-data')
    except IOError as e:
        pytest.fail(f"Error opening test image: {str(e)}")
    
    assert response.status_code == 200
    assert 'name' in response.json

if __name__ == '__main__':
    pytest.main([__file__])