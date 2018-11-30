import server
import pytest

from unittesting.fixtures.user import user_default_data
from logic.db import get_or_create, authenticate

from models.user import User

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture
def app():
    return server.get_app()


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


class Request:
    def __init__(self, json):
        self.json = json


async def test_authenticate_user(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test'

    request = Request(data)
    user = await authenticate(request)

    assert user.get('user_id') == user_obj.id
    assert user.get('username') == user_obj.username

    # delete user from db
    await user_obj.delete()


async def test_authenticate_invalid_username(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test1'

    request = Request(data)
    catch_error = False
    try:
        await authenticate(request)
    except Exception as ex:
        assert str(ex) == 'Password is incorrect.'
        catch_error = True

    assert catch_error is True

    # delete user from db
    await user_obj.delete()


async def test_authenticate_invalid_password(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    data['password'] = 'test1'

    request = Request(data)
    catch_error = False
    try:
        await authenticate(request)
    except Exception as ex:
        assert str(ex) == "Password is incorrect."
        catch_error = True

    assert catch_error is True

    # delete user from db
    await user_obj.delete()


async def test_authenticate_miss_password(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    # make shallow copy and change hash pass to clear pass
    data = user_default_data.copy()
    del data['full_name']
    del data['password']

    request = Request(data)
    catch_error = False
    try:
        await authenticate(request)
    except Exception as ex:
        assert str(ex) == "Missing username or password."
        catch_error = True

    assert catch_error is True

    # delete user from db
    await user_obj.delete()


async def test_create_object_with_get_or_create(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    _user_obj = await User.query.where(*(User.username == user_default_data.get('username'), )).gino.first()

    assert _user_obj
    assert _user_obj.id == user_obj.id
    assert _user_obj.username == user_obj.username

    await user_obj.delete()


async def test_get_object_with_get_or_create(test_cli):
    # create user object
    user_obj = await get_or_create(User, None, **user_default_data)

    user_obj2 = await get_or_create(User, *(User.username == user_default_data.get('username'), ), **user_default_data)

    _user_obj = await User.query.where(*(User.username == user_default_data.get('username'), )).gino.first()

    assert _user_obj
    assert _user_obj.id == user_obj2.id
    assert _user_obj.username == user_obj2.username

    await user_obj.delete()

