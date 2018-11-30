import server
import pytest

from unittesting.fixtures.user import user_default_data

from logic.user import create_user, retrieve_user
from logic.db import get_or_create, delete

from models.user import User

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture
def app():
    return server.get_app()


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


async def test_retrieve_user(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    user = await retrieve_user(None, {'user_id': user_obj.id})

    assert user
    assert user.get('username') == user_obj.username
    assert user.get('user_id') == user_obj.id

    # delete user
    await user_obj.delete()


async def test_retrieve_user_with_invalid_user_id(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    user = await retrieve_user(None, {'user_id': 0})

    assert not user

    # delete user
    await user_obj.delete()


async def test_retrieve_user_without_payload(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    user = await retrieve_user(None, None)

    assert not user

    # delete user
    await user_obj.delete()


async def test_create_user(test_cli):
    # create user object
    user_obj, error = await create_user(**user_default_data)

    assert not error
    assert user_obj.get('username') == user_default_data.get('username')

    # delete user
    await delete(User, *(User.username == user_default_data.get('username'), ))


async def test_create_duplicate_user(test_cli):
    # create user object
    await create_user(**user_default_data)
    user_obj, error = await create_user(**user_default_data)

    assert error
    assert not user_obj
    assert error == "User exists"

    # delete user
    await delete(User, *(User.username == user_default_data.get('username'), ))

