from tinydb import TinyDB, Query
from app.utils.logger import setup_logger

class UserDAO:
    def __init__(self, db_file, log_folder):
        self.db = TinyDB(db_file)
        self.users_table = self.db.table('users')
        self.logger = setup_logger('user_dao', log_folder)

    def get_user_by_username(self, username):
        User = Query()
        user = self.users_table.get(User.username == username)
        self.logger.info(f"Retrieved user: {username}")
        return user

    def get_user_by_id(self, user_id):
        if not isinstance(user_id, (int, str)):
            self.logger.error(f"Invalid user_id type: {type(user_id)}")
            return None
        try:
            user = self.users_table.get(doc_id=int(user_id))
            self.logger.info(f"Retrieved user with id: {user_id}")
            return user
        except ValueError:
            self.logger.error(f"Invalid user_id value: {user_id}")
            return None

    def create_user(self, user_data):
        user_id = self.users_table.insert(user_data)
        self.logger.info(f"Created new user with id: {user_id}")
        return user_id

    def update_user(self, user_id, update_data):
        self.users_table.update(update_data, doc_ids=[int(user_id)])
        self.logger.info(f"Updated user with id: {user_id}")