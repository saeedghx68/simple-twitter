import server
import pytest
import json

from unittesting.fixtures.user import user_default_data

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


async def test_search_tweet(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)
    tag_obj = await get_or_create(Tag, None, **{'tag_name': 'tag1'})
    tweet_obj = await get_or_create(Tweet, None, **{'msg': 'test msg', 'user_id': user_obj.id})
    tag_tweet_obj = await get_or_create(TagTweet, None, **{'tag_id': tag_obj.id, 'tweet_id': tweet_obj.id})

    # delete key and values from redis
    await delete_key(tag_obj.tag_name)

    # make shallow copy and change hash pass to clear pass
    user_data = user_default_data.copy()
    del user_data['full_name']
    user_data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(user_data))
    assert resp.status == 200

    headers = {'AUTHORIZATION': f'Bearer {(await resp.json()).get("access_token")}'}

    resp = await test_cli.get('/api/v1/search-tweets?tag=tag1', headers=headers)
    assert resp.status == 200

    result = await resp.json()

    assert result.get('code') == 'success'
    assert result.get('pagination') == {'total': 1, 'page': 1, 'page_size': 10}
    assert result.get('data') == [tweet_obj.as_json()]

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


async def test_search_tweet_empty_tag(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)
    tag_obj = await get_or_create(Tag, None, **{'tag_name': 'tag1'})
    tweet_obj = await get_or_create(Tweet, None, **{'msg': 'test msg', 'user_id': user_obj.id})
    tag_tweet_obj = await get_or_create(TagTweet, None, **{'tag_id': tag_obj.id, 'tweet_id': tweet_obj.id})

    # make shallow copy and change hash pass to clear pass
    user_data = user_default_data.copy()
    del user_data['full_name']
    user_data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(user_data))
    assert resp.status == 200

    headers = {'AUTHORIZATION': f'Bearer {(await resp.json()).get("access_token")}'}

    resp = await test_cli.get('/api/v1/search-tweets?tag=', headers=headers)
    assert resp.status == 400

    result = await resp.json()

    assert result.get('code') == 'badRequest'
    assert result.get('message') == 'Bad request'

    # delete objects
    await tag_tweet_obj.delete()
    await tag_obj.delete()
    await tweet_obj.delete()
    await user_obj.delete()


async def test_search_tweet_without_tag(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)
    tag_obj = await get_or_create(Tag, None, **{'tag_name': 'tag1'})
    tweet_obj = await get_or_create(Tweet, None, **{'msg': 'test msg', 'user_id': user_obj.id})
    tag_tweet_obj = await get_or_create(TagTweet, None, **{'tag_id': tag_obj.id, 'tweet_id': tweet_obj.id})

    # make shallow copy and change hash pass to clear pass
    user_data = user_default_data.copy()
    del user_data['full_name']
    user_data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(user_data))
    assert resp.status == 200

    headers = {'AUTHORIZATION': f'Bearer {(await resp.json()).get("access_token")}'}

    resp = await test_cli.get('/api/v1/search-tweets?', headers=headers)
    assert resp.status == 400

    result = await resp.json()

    assert result.get('code') == 'badRequest'
    assert result.get('message') == 'Bad request'

    # delete objects
    await tag_tweet_obj.delete()
    await tag_obj.delete()
    await tweet_obj.delete()
    await user_obj.delete()
