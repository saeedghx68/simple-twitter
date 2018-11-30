from utils import utils
from models.user import User
from utils.logger import global_logger


async def create_user(username, password, full_name):
    """
    create user if exist return a dictionary with user is None
    :param username: user username
    :param password: user password
    :param full_name: user full name
    :return: a dictionary which contains user dictionary and a msg
    """
    try:
        if await User.query.where(User.username == username).gino.first():
            return None, "User exists"
        user = User(
            username=username,
            password=utils.hash_password(password),
            full_name=full_name)
        await user.create()
        return user.as_json(), None
    except Exception as ex:
        global_logger.write_log('error', f"error: {ex}")
        return None, ex


async def retrieve_user(request, payload, *args, **kwargs):
    """
    useful for inject_user decorator to fetch logged in user
    :param request:
    :param payload: has user data
    :param args:
    :param kwargs:
    :return: User json object
    """
    if payload:
        user_id = payload.get('user_id', None)
        user = await User.query.where(User.id == user_id).gino.first()
        if not user:
            return None
        return user.as_json()
    else:
        return None
