import server
import pytest

from logic.redis import get_values, append_value, delete_key, get_value

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture
def app():
    return server.get_app()


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


async def test_append_redis_and_get_value(test_cli):
    # create user object
    await append_value('key1', 'value1')
    value = await get_value('key1')
    assert value == 'value1'

    # delete key and values from redis
    await delete_key('key1')


async def test_append_some_values_redis_and_get_values(test_cli):
    # create user object
    await append_value('key1', 'value1')
    await append_value('key1', 'value2')
    await append_value('key1', 'value3')
    await append_value('key1', 'value2')
    values, total, error = await get_values('key1', 1, 10)
    assert values == ['value1', 'value2', 'value3', 'value2']
    assert total == 4
    assert not error

    # delete key and values from redis
    await delete_key('key1')