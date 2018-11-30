import server
import pytest

from unittesting.fixtures.user import user_default_data
from unittesting.fixtures.tweet import tweet_default_data

from logic.tweet import add_tweet, fetch_tweets
from logic.db import get_or_create
from logic.redis import get_values, delete_key

from models.user import User
from models.tweet import Tweet
from models.tag import Tag
from models.tag_tweet import TagTweet

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture
def app():
    return server.get_app()


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


async def test_add_tweet(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)
    tweet_data, error = await add_tweet(user_obj.as_json(), tweet_default_data.get('msg'), tweet_default_data.get('tags'))

    # find tag object and check it
    tag_obj = await get_or_create(Tag, *(Tag.tag_name == tweet_default_data.get('tags')[0], ), **{})
    assert tag_obj
    assert tag_obj.tag_name == tweet_default_data.get('tags')[0]

    # find tweet object and check msg and related to user
    tweet_obj = await get_or_create(Tweet, *(Tweet.user_id == user_obj.id, ), **{})
    assert tweet_obj
    assert tweet_obj.msg == tweet_data.get('msg')
    assert tweet_obj.user_id == user_obj.id

    # find tweet_tag object and check exist and check related tweet id
    tag_tweet_obj = await get_or_create(TagTweet, *(TagTweet.tag_id == tag_obj.id, ), **{})
    assert tag_tweet_obj
    assert tag_tweet_obj.tweet_id == tweet_obj.id

    # check redis key and values
    result, total, error = await get_values(tag_obj.tag_name, 1, 10)
    assert result == [tweet_obj.as_json()]
    assert total == 1
    assert not error

    # delete objects
    await tag_tweet_obj.delete()
    await tag_obj.delete()
    await tweet_obj.delete()
    await user_obj.delete()

    # delete key and values from redis
    await delete_key(tag_obj.tag_name)


async def test_search_tweets(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)
    tag_obj = await get_or_create(Tag, None, **{'tag_name': 'tag1'})
    tweet_obj = await get_or_create(Tweet, None, **{'msg': 'test msg', 'user_id': user_obj.id})
    tag_tweet_obj = await get_or_create(TagTweet, None, **{'tag_id': tag_obj.id, 'tweet_id': tweet_obj.id})

    # delete key and values from redis
    await delete_key(tag_obj.tag_name)

    result, total, error = await fetch_tweets(tag_obj.tag_name, 1, 10)
    assert result == [tweet_obj.as_json()]
    assert total == 1
    assert not error

    # delete objects
    await tag_tweet_obj.delete()
    await tag_obj.delete()
    await tweet_obj.delete()
    await user_obj.delete()

    # delete key and values from redis
    await delete_key(tag_obj.tag_name)


async def test_search_tweets_without_data(test_cli):

    # delete key and values from redis
    await delete_key('tag2')

    result, total, error = await fetch_tweets('tag2', 1, 10)
    assert result == []
    assert total == 0
    assert not error
