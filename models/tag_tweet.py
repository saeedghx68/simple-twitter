from base.base_model import BaseClass
from app import db


class TagTweet(BaseClass):
    __tablename__ = 'tag_tweet'

    tag_id = db.Column(db.ForeignKey('tags.id'))
    tweet_id = db.Column(db.ForeignKey('tweets.id'))

    def __str__(self):
        return f'{self.tag_id} - {self.tweet_id}'
