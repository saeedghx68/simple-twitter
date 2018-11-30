from sanic import Sanic
from gino.ext.sanic import Gino
from gino.crud import CRUDModel, UpdateRequest, DEFAULT
from datetime import datetime
import settings
import uvloop
import asyncio


class HookedUpdateRequest(UpdateRequest):
    async def apply(self, bind=None, timeout=DEFAULT):
        self.update(last_modified=datetime.utcnow())
        return await super().apply(bind, timeout)


class HookedCRUDModel(CRUDModel):
    _update_request_cls = HookedUpdateRequest  # requires latest master


db = Gino(model_classes=(HookedCRUDModel,))
app = Sanic(__name__)
db.init_app(app)

# load app settings
settings.app.load_settings(app, db)

# create uvloop to db set bind and create all tables
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
loop.run_until_complete(db.set_bind(app.config.DB_CONN_STR))

# loads model to create tables
from models.user import User
from models.tweet import Tweet
from models.tag import Tag
from models.tag_tweet import TagTweet
loop.run_until_complete(db.gino.create_all())