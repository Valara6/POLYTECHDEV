from flask_login import current_user

class CheckRights:
    def __init__(self, record):
        self.record = record

    def create_auction(self):
        return current_user.is_admin()

    def add_item(self):
        return current_user.is_seller()