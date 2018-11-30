from base.base_model import BaseClass
from app import db


class User(BaseClass):
    __tablename__ = 'users'

    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(128), nullable=False)

    def as_json(self):
        return {
            "user_id": self.id,
            "username": self.username,
            "full_name": self.full_name,
        }

    def __str__(self):
        return f'{self.username}'
