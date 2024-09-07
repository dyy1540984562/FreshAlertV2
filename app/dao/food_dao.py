from tinydb import TinyDB, Query
from app.utils.logger import setup_logger

class FoodDAO:
    def __init__(self, db_file, log_folder):
        self.db = TinyDB(db_file)
        self.foods_table = self.db.table('foods')
        self.logger = setup_logger('food_dao', log_folder)

    def get_foods(self, user_id):
        Food = Query()
        foods = self.foods_table.search(Food.user_id == str(user_id))
        self.logger.info(f"Retrieved {len(foods)} foods for user {user_id}")
        return foods

    def add_food(self, food_data):
        food_id = self.foods_table.insert(food_data)
        self.logger.info(f"Added new food with id: {food_id}")
        return food_id

    def delete_food(self, food_id, user_id):
        Food = Query()
        result = self.foods_table.remove((Food.id == food_id) & (Food.user_id == str(user_id)))
        self.logger.info(f"Deleted food with id: {food_id} for user {user_id}")
        return result