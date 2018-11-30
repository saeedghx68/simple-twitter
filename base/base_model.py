from datetime import datetime
from app import db


class BaseClass(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    last_modified = db.Column(db.DateTime())
