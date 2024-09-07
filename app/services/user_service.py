from app.dao.user_dao import UserDAO
from app.utils.logger import setup_logger

class UserService:
    def __init__(self, config):
        self.user_dao = UserDAO(config.DB_FILE, config.LOG_FOLDER)
        self.logger = setup_logger('user_service', config.LOG_FOLDER)

    def register(self, username, password):
        existing_user = self.user_dao.get_user_by_username(username)
        if existing_user:
            self.logger.warning(f"Registration failed: Username {username} already exists")
            return None

        user_id = self.user_dao.create_user({
            'username': username,
            'password': password
        })
        self.logger.info(f"User registered successfully: {username}")
        return {"id": user_id, "username": username}

    def login(self, username, password):
        user = self.user_dao.get_user_by_username(username)
        if user and user['password'] == password:
            self.logger.info(f"User logged in successfully: {username}")
            return {"id": user.doc_id, "username": user['username']}
        self.logger.warning(f"Login failed for user: {username}")
        return None

    def change_password(self, user_id, new_password):
        if user_id is None:
            self.logger.error("Attempt to change password with None user_id")
            return False
        user = self.user_dao.get_user_by_id(user_id)
        if user:
            self.user_dao.update_user(user_id, {'password': new_password})
            self.logger.info(f"Password changed for user id: {user_id}")
            return True
        self.logger.warning(f"Password change failed for user id: {user_id}")
        return False

    def add_secret_key(self, user_id, provider, secret_key):
        user = self.user_dao.get_user_by_id(user_id)
        if user:
            self.user_dao.update_user(user_id, {
                'secret_key': secret_key,
                'secret_key_provider': provider
            })
            self.logger.info(f"Secret key added for user id: {user_id}")
            return True
        self.logger.warning(f"Adding secret key failed for user id: {user_id}")
        return False