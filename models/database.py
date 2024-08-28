from tinydb import TinyDB, Query
from datetime import datetime

class Database:
    def __init__(self, filename):
        self.db = TinyDB(filename)
        self.User = Query()

    def add_user(self, username, password):
        if not self.db.search(self.User.username == username):
            self.db.insert({'username': username, 'password': password, 'foods': []})
            return True
        return False

    def check_user(self, username, password):
        return self.db.search((self.User.username == username) & (self.User.password == password))

    def add_food(self, username, name, label, production_date, expiry_date):
        user = self.db.get(self.User.username == username)
        if user:
            user['foods'].append({'name': name, 'label': label, 'production_date': production_date, 'expiry_date': expiry_date})
            self.db.update(user, self.User.username == username)
            return True
        return False

    def get_all_foods(self, username):
        user = self.db.get(self.User.username == username)
        return user['foods'] if user else []

    def delete_food(self, username, food_name):
        user = self.db.get(self.User.username == username)
        if user:
            user['foods'] = [food for food in user['foods'] if food['name'] != food_name]
            self.db.update(user, self.User.username == username)
            return True
        return False
