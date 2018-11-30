import server
import pytest
import json

from unittesting.fixtures.user import user_default_data
from logic.db import get_or_create
from models.user import User

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture
def app():
    return server.get_app()


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


async def test_fetch_user(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(data))
    assert resp.status == 200

    headers = {'AUTHORIZATION': f'Bearer {(await resp.json()).get("access_token")}'}

    resp = await test_cli.get('/api/v1/me', headers=headers)

    assert resp.status == 200

    result = (await resp.json()).get('me')
    del result['user_id']

    assert result == {'username': 'test', 'full_name': 'test'}

    # delete user from db
    await user_obj.delete()


async def test_fetch_user_invalid_token(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(data))
    assert resp.status == 200

    invalid_token = (await resp.json()).get("access_token")
    invalid_token = invalid_token[:-4] + 'abcd'
    headers = {'AUTHORIZATION': f'Bearer {invalid_token}'}

    resp = await test_cli.get('/api/v1/me', headers=headers)

    assert resp.status == 401

    result = await resp.json()

    assert result.get('reasons') == ["Auth required."]
    assert result.get('exception') == "Unauthorized"

    # delete user from db
    await user_obj.delete()


async def test_fetch_user_without_header(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(data))
    assert resp.status == 200

    resp = await test_cli.get('/api/v1/me')

    assert resp.status == 401

    result = await resp.json()

    assert result.get('reasons') == ["Authorization header not present."]
    assert result.get('exception') == "Unauthorized"

    # delete user from db
    await user_obj.delete()


async def test_fetch_user_with_empty_header(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(data))
    assert resp.status == 200

    resp = await test_cli.get('/api/v1/me', headers={'AUTHORIZATION': ''})

    assert resp.status == 401

    result = await resp.json()

    assert result.get('reasons') == ["Authorization header is invalid."]
    assert result.get('exception') == "Unauthorized"

    # delete user from db
    await user_obj.delete()
