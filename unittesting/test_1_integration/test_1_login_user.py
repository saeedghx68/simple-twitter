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


async def test_login_user(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(data))
    assert resp.status == 200

    resp_json = await resp.json()

    assert resp_json.get('access_token')
    assert resp_json.get('access_token') != ''

    # delete user from db
    await user_obj.delete()


async def test_login_invalid_username(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test'
    data['username'] = 'test2'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(data))
    resp_json = await resp.json()

    assert resp.status == 401
    assert resp_json.get('reasons') == ['User not found.']
    assert resp_json.get('exception') == 'AuthenticationFailed'

    # delete user from db
    await user_obj.delete()


async def test_login_invalid_password(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test2'

    resp = await test_cli.post('/api/v1/login', data=json.dumps(data))
    resp_json = await resp.json()

    assert resp.status == 401
    assert resp_json.get('reasons') == ['Password is incorrect.']
    assert resp_json.get('exception') == 'AuthenticationFailed'

    # delete user from db
    await user_obj.delete()


async def test_login_without_data(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    data = {}

    resp = await test_cli.post('/api/v1/login', data=json.dumps(data))
    resp_json = await resp.json()

    assert resp.status == 401

    assert resp_json.get('reasons') == ['Missing username or password.']
    assert resp_json.get('exception') == 'AuthenticationFailed'

    # delete user from db
    await user_obj.delete()
