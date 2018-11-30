from base.base_model import BaseClass
from app import db


class Tag(BaseClass):
    __tablename__ = 'tags'

    tag_name = db.Column(db.String(64), nullable=False)

    def __str__(self):
        return f'{self.tag_name}'
