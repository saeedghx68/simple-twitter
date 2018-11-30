import server
import pytest
import json
from models.user import User

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture
def app():
    return server.get_app()


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


async def test_register_user(test_cli):
    data = {
        'username': 'test',
        'password': 'test',
        'full_name': 'test'
    }
    resp = await test_cli.post('/api/v1/register', data=json.dumps(data))
    assert resp.status == 201

    resp_json = await resp.json()

    # check response data
    assert resp_json.get('data').get('username') == data['username']
    assert resp_json.get('code') == 'success'

    # check user db
    user = await User.query.where(User.username == data['username']).gino.first()
    assert user.username == data['username']

    # delete user from db
    await User.delete.where(User.username == data['username']).gino.status()


async def test_register_user_exist(test_cli):
    data = {
        'username' : 'test',
        'password': 'test',
        'full_name': 'test'
    }
    resp = await test_cli.post('/api/v1/register', data=json.dumps(data))
    assert resp.status == 201
    resp = await test_cli.post('/api/v1/register', data=json.dumps(data))
    assert resp.status == 422
    await User.delete.where(User.username == data['username']).gino.status()


async def test_register_invalid_data(test_cli):
    data = {
        'username': 'test2',
    }
    resp = await test_cli.post('/api/v1/register', data=json.dumps(data))
    assert resp.status == 400


async def test_register_no_data(test_cli):
    resp = await test_cli.post('/api/v1/register')
    assert resp.status == 400
