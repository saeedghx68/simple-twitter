from sqlalchemy import func

from . import redis
from .db import get_or_create
from models.tweet import Tweet
from models.tag import Tag
from models.tag_tweet import TagTweet
from app import db
from utils.logger import global_logger


async def add_tweet(user, msg, tags):
    """
    add user tweet with specific tags and after that add to redis to fetch in future
    :param user: login user json data
    :param msg: tweet message
    :param tags: list of tags
    :return:
    """
    try:
        async with db.transaction():
            tweet = Tweet(msg=msg, user_id=user.get('user_id'))
            await tweet.create()
            for tag_item in tags:
                tag = await get_or_create(Tag, *(Tag.tag_name == tag_item,), **({"tag_name": tag_item}))
                tweet_tag = TagTweet(tag_id=tag.id, tweet_id=tweet.id)
                await tweet_tag.create()
                if tweet_tag:
                    await redis.append_value(tag.tag_name, tweet.as_json())
        return tweet.as_json(), None
    except Exception as ex:
        global_logger.write_log('error', f"error: {ex}")
        return None, ex


async def fetch_tweets(tag, page=1, page_size=10):
    """
    At the first lookup in redis if does not exist, search on PG
    in pg run this sql query => SELECT * FROM tweets WHERE tweets.id IN
                            (SELECT tweet_id FROM tag_tweet WHERE tag_tweet.tag_id =
                            (SELECT tags.id FROM tags WHERE tags.tag_name={tag}))
                            limit {page_size} offset (page - 1) * page_size
    fetch all of tweets which related with specific tag
    :param tag: tag name
    :param page: page number
    :param page_size: page_size
    :return: A list of tweet and total count
    """
    # fetch from redis
    result, total, error = await redis.get_values(tag, page, page_size)
    if total and result:
        return result, total, error

    try:
        # If does not exist in redis after that search in pg
        # select count of tweets record
        q_total = db.select([func.count(Tweet.id)]).where(
            Tweet.id.in_(
                db.select([TagTweet.tweet_id]).where(
                    TagTweet.tag_id ==
                    db.select([Tag.id]).where(Tag.tag_name == tag)
                )
            )
        )
        total = await q_total.gino.model(Tweet).scalar()

        # If there aren't any records then return [], 0
        if not total:
            return [], total, None

        # select Tweet.id, Tweet.msg, Tweet.user_id of tweets record
        q_data = db.select(
            [Tweet.id, Tweet.msg, Tweet.user_id, Tweet.created_at]
        ).where(
            Tweet.id.in_(
                db.select([TagTweet.tweet_id]).where(
                    TagTweet.tag_id ==
                    db.select([Tag.id]).where(Tag.tag_name == tag)
                )
            )
        ).limit(page_size).offset((page - 1) * page_size)
        result = []
        tweets = await q_data.gino.model(Tweet).all()

        for item in tweets:
            result.append(item.as_json())
            # add key and value to redis
            await redis.append_value(tag, item.as_json())

        return result, total, None
    except Exception as ex:
        global_logger.write_log('error', f"error: {ex}")
        return None, None, ex
