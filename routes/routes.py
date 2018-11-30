from sanic_openapi import swagger_blueprint, openapi_blueprint, doc
from sanic_jwt import initialize, protected, inject_user, configuration
from sanic.blueprints import Blueprint

from app import app
from utils.swagger_doc import UserSwDoc, TweetSwDoc
from logic.db import authenticate
from logic.user import create_user, retrieve_user
from logic.tweet import add_tweet, fetch_tweets
from utils import jwt as jwt_utils
from utils import response

blueprint = Blueprint('Twitter', '/api/v1')


@blueprint.post("/register")
@doc.summary("Creates a user")
@doc.consumes(UserSwDoc, location="body")
@doc.produces(UserSwDoc)
@doc.tag('auth_bp')
async def register(request):
    if not request.json:
        return response.response_with(response.BAD_REQUEST_400)
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    full_name = request.json.get('full_name', None)
    if not(username and password and full_name):
        return response.response_with(response.BAD_REQUEST_400)
    result, error = await create_user(username, password, full_name)
    if error:
        return response.response_with(response.INVALID_INPUT_422, error=error)
    return response.response_with(response.SUCCESS_201, value={"data": result},)


@blueprint.post("/tweet")
@doc.consumes(TweetSwDoc, location="body")
@doc.produces(TweetSwDoc)
@doc.consumes({'AUTHORIZATION': str}, location='header')
@protected()
@inject_user()
async def tweet(request, user):
    if not request.json:
        return response.response_with(response.BAD_REQUEST_400)
    tags = request.json.get('tags', None)
    msg = request.json.get('msg', None)
    if not(tags and msg):
        return response.response_with(response.BAD_REQUEST_400)
    result, error = await add_tweet(user, msg, tags)
    if error:
        return response.response_with(response.SERVER_ERROR_500, error=error)
    return response.response_with(response.SUCCESS_201, value={"data": result},)


@blueprint.get("/search-tweets")
@doc.consumes({'tag': str})
@doc.consumes({'page': int})
@doc.consumes({'page_size': int})
@doc.consumes({'AUTHORIZATION': str}, location='header')
@protected()
async def search_tweets(request):
    if not request.args:
        return response.response_with(response.BAD_REQUEST_400)
    tag = request.args.get('tag', None)
    page_size = request.args.get('page_size', 10)
    page = request.args.get('page', 1)
    if not(tag and page_size and page):
        response.response_with(response.BAD_REQUEST_400)
    result, total, error = await fetch_tweets(tag, int(page), int(page_size))
    if error:
        return response.response_with(response.SERVER_ERROR_500, error=error)
    return response.response_with(
        response.SUCCESS_200,
        value={"data": result},
        pagination={
            'total': total,
            'page': page,
            'page_size': page_size,
        }
    )

app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
app.blueprint(blueprint)
jwt_utils.add_swagger_doc()

initialize(app,
           path_to_authenticate='/login',
           authenticate=authenticate,
           retrieve_user=retrieve_user,
           api_version=app.config.API_VERSION,
           url_prefix='/api/v1',
           blueprint_name='authentication'
           )

configuration.defaults['blueprint_name'] = 'authentication'


def load_router():
    print('load router ...')