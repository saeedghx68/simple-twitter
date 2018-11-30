import server
import pytest
import json

from unittesting.fixtures.user import user_default_data
from unittesting.fixtures.tweet import tweet_default_data

from logic.db import get_or_create
from logic.redis import delete_key, get_values

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


async def test_user_tweet(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    user_data = user_default_data.copy()
    del user_data['full_name']
    user_data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(user_data))
    assert resp.status == 200

    headers = {'AUTHORIZATION': f'Bearer {(await resp.json()).get("access_token")}'}

    resp = await test_cli.post('/api/v1/tweet', data=json.dumps(tweet_default_data), headers=headers)

    assert resp.status == 201

    result = await resp.json()

    assert result.get('code') == 'success'

    tweet_data = result.get('data')

    assert tweet_data.get('user_id') == user_obj.id
    assert tweet_data.get('msg') == tweet_data.get('msg')

    # find tag object and check it
    tag_obj = await get_or_create(Tag, *(Tag.tag_name == tweet_default_data.get('tags')[0], ), **{})
    assert tag_obj
    assert tag_obj.tag_name == tweet_default_data.get('tags')[0]

    # find tweet object and check msg and related to user
    tweet_obj = await get_or_create(Tweet, *(Tweet.user_id == user_obj.id,), **{})
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


async def test_user_tweet_without_tags(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    user_data = user_default_data.copy()
    del user_data['full_name']
    user_data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(user_data))
    assert resp.status == 200

    headers = {'AUTHORIZATION': f'Bearer {(await resp.json()).get("access_token")}'}

    tweet_body = tweet_default_data.copy()
    del tweet_body['tags']
    resp = await test_cli.post('/api/v1/tweet', data=json.dumps(tweet_body), headers=headers)

    assert resp.status == 400

    result = await resp.json()
    assert result.get('code') == 'badRequest'
    assert result.get('message') == 'Bad request'

    # delete objects
    await user_obj.delete()


async def test_user_tweet_without_msg(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    user_data = user_default_data.copy()
    del user_data['full_name']
    user_data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(user_data))
    assert resp.status == 200

    headers = {'AUTHORIZATION': f'Bearer {(await resp.json()).get("access_token")}'}

    tweet_body = tweet_default_data.copy()
    del tweet_body['msg']
    resp = await test_cli.post('/api/v1/tweet', data=json.dumps(tweet_body), headers=headers)

    assert resp.status == 400

    result = await resp.json()
    assert result.get('code') == 'badRequest'
    assert result.get('message') == 'Bad request'

    # delete objects
    await user_obj.delete()
