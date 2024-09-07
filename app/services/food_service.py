from datetime import datetime, timedelta
from app.dao.food_dao import FoodDAO
from app.utils.food_recognizer import FoodRecognizer
from app.utils.logger import setup_logger

class FoodService:
    def __init__(self, config):
        self.food_dao = FoodDAO(config.DB_FILE, config.LOG_FOLDER)
        self.food_recognizer = FoodRecognizer(config.KIMI_API_KEY, config.LOG_FOLDER)
        self.logger = setup_logger('food_service', config.LOG_FOLDER)

    def get_foods(self, user_id):
        foods = self.food_dao.get_foods(user_id)
        for food in foods:
            food['daysLeft'] = self._calculate_days_left(food['expirationDate'])
        return sorted(foods, key=lambda x: x['daysLeft'])

    def add_food(self, food_data, image_path=None):
        food_data['expirationDate'] = self._calculate_expiration_date(
            food_data['productionDate'], 
            int(food_data['shelfLife'])  # 确保 shelfLife 是整数
        )
        food_data['daysLeft'] = self._calculate_days_left(food_data['expirationDate'])
        
        if image_path:
            food_data['imagePath'] = image_path

        food_id = self.food_dao.add_food(food_data)
        food_data['id'] = food_id
        return food_data

    def delete_food(self, food_id, user_id):
        return self.food_dao.delete_food(food_id, user_id)

    def recognize_food(self, image_path, user_id):
        return self.food_recognizer.recognize_with_kimi(image_path, user_id)

    @staticmethod
    def _calculate_expiration_date(production_date, shelf_life):
        prod_date = datetime.strptime(production_date, "%Y-%m-%d")
        return (prod_date + timedelta(days=shelf_life)).strftime("%Y-%m-%d")

    @staticmethod
    def _calculate_days_left(expiration_date):
        today = datetime.now().date()
        exp_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        return (exp_date - today).days