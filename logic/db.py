from sanic_jwt import exceptions
from models.user import User
from utils.utils import hash_password
from utils.logger import global_logger


async def authenticate(request, *args, **kwargs):
    """
    to authenticate JWT for generating token
    :param request:
    :param args: has post data
    :param kwargs:
    :return: user json data
    """
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")

    user = await User.query.where(User.username == username).gino.first()
    if user is None:
        raise exceptions.AuthenticationFailed("User not found.")

    if hash_password(password) != user.password:
        raise exceptions.AuthenticationFailed("Password is incorrect.")

    return user.as_json()


async def get_or_create(model, *args, **kwargs):
    """
    get or create method for using at the first create object if exist return object
    :param model: model class
    :param args: where condition
    :param kwargs: for setting model attribute to create object
    :return: model instance
    """
    try:
        if args:
            instance = await model.query.where(*args).gino.first()
        if not instance and kwargs:
            instance = model(**kwargs)
            await instance.create()
            return instance
        return instance
    except Exception as ex:
        global_logger.write_log('error', f"error: {ex}")
        return None


async def delete(model, *args):
    """
    delete method for using delete a record from model
    :param model: model class
    :param args: where condition
    :return:
    """
    try:
        await model.delete.where(*args).gino.status()
    except Exception as ex:
        global_logger.write_log('error', f"error: {ex}")