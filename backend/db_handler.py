from flask_sqlalchemy import SQLAlchemy

class DBHandler:
    def __init__(self):
        self.db = SQLAlchemy()

    def init_app(self, app):
        self.db.init_app(app)

    def create_all(self):
        self.db.create_all()

    def get_session(self):
        return self.db.session
