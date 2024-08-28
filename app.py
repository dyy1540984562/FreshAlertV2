from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.database import Database
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 请使用一个安全的随机字符串

db = Database('users.json')  # 修改为 users.json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('query', '')
    username = session['username']
    all_foods = db.get_all_foods(username)
    
    # 简单的搜索实现，你可以根据需要改进
    foods = [food for food in all_foods if query.lower() in food['name'].lower()]
    
    return render_template('food_list.html', foods=foods, search_query=query)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.check_user(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.add_user(username, password):
            flash('User registered successfully')
            return redirect(url_for('login'))
        else:
            flash('Username already exists')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    foods = db.get_all_foods(username)
    expired_foods = [food for food in foods if datetime.strptime(food['expiry_date'], '%Y-%m-%d') < datetime.now()]
    return render_template('food_list.html', foods=foods, expired_foods=expired_foods)

@app.route('/add_food', methods=['POST'])
def add_food():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # 字段检查
    required_fields = ['name', 'production_date', 'shelf_life']
    for field in required_fields:
        if field not in request.form or not request.form[field]:
            flash(f'Please provide {field}.')
            return redirect(url_for('dashboard'))
    
    username = session['username']
    name = request.form['name']
    production_date = request.form['production_date']
    shelf_life = request.form['shelf_life']
    label = request.form.get('label', '')  # 可选字段
    
    # 数据验证
    try:
        prod_date = datetime.strptime(production_date, '%Y-%m-%d')
        shelf_days = int(shelf_life)
    except ValueError:
        flash('Invalid date format or shelf life value.')
        return redirect(url_for('dashboard'))
    
    # 计算过期日期
    expiry_date = (prod_date + timedelta(days=shelf_days)).strftime('%Y-%m-%d')
    
    # 添加食品到数据库
    if db.add_food(username, name, label, production_date, expiry_date):
        flash('Food item added successfully.')
    else:
        flash('Failed to add food item.')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_food/<name>', methods=['POST'])
def delete_food(name):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    db.delete_food(username, name)
    return redirect(url_for('dashboard'))

@app.route('/expired_foods')
def expired_foods():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    foods = db.get_all_foods(username)
    expired_foods = [food for food in foods if datetime.strptime(food['expiry_date'], '%Y-%m-%d') < datetime.now()]
    return render_template('food_expired.html', expired_foods=expired_foods)
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)