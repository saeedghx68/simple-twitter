from base.base_model import BaseClass
from app import db


class Tweet(BaseClass):
    __tablename__ = 'tweets'

    msg = db.Column(db.String(280), nullable=False)
    user_id = db.Column(None, db.ForeignKey('users.id'))

    def __str__(self):
        return f'{self.user_id} -> {self.msg}'

    def as_json(self):
        return {
            "id": self.id,
            "msg": self.msg,
            "user_id": self.user_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }