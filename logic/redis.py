from app import app
from utils.logger import global_logger


async def append_value(key, msg):
    """
    append value to redis
    :param key: redis key
    :param msg: tweet object as json
    :return:
    """
    await app.redis_pool.append(key, f'{repr(msg)};')


async def delete_key(key):
    """
    delete key and values
    :param key: redis key
    :return:
    """
    await app.redis_pool.delete(key)


async def get_value(key):
    """
    get value
    :param key: redis key
    :return: redis value
    """
    return eval((await app.redis_pool.get(key)).decode('utf-8').split(";")[0])


async def get_values(key, page, page_size):
    """
    fetch values from a specific key and return as
    :param key: redis key to fetch values
    :param page: page number
    :param page_size: page size
    :return:
    """
    result = []
    total = 0
    error = None
    try:
        values = await app.redis_pool.get(key)
        if values:
            start = (page - 1) * page_size
            result = values.decode('utf-8').split(';')[:-1]
            total = len(result)
            result = [eval(item) for item in result[start: start + page_size]]
    except Exception as ex:
        global_logger.write_log('error', f"error: {ex}")
        error = ex
    finally:
        return result, total, error
