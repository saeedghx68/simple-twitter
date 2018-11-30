import aioredis
from app import app
from routes import routes


@app.listener('before_server_start')
async def before_server_start(app, loop):
    # create redis pool connection and set app config to access anywhere
    app.redis_pool = await aioredis.create_redis_pool(
        (app.config.REDIS_HOST, app.config.REDIS_PORT),
        minsize=5,
        maxsize=10,
        loop=loop,
    )


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    app.redis_pool.close()
    await app.redis_pool.wait_closed()


def get_app():
    """
    for using unittest
    :return: app
    """
    routes.load_router()
    return app


if __name__ == "__main__":
    routes.load_router()
    app.static('/', './')
    app.run(host="0.0.0.0", port=2080, debug=app.config.DEBUG, workers=int(app.config.WORKERS))
