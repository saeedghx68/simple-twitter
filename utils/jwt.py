from sanic_jwt.endpoints  import AuthenticateEndpoint, RetrieveUserEndpoint, VerifyEndpoint, RefreshEndpoint
from sanic_openapi import doc
from sanic_jwt import initialize, protected, inject_user
from utils.swagger_doc import LoginSwDoc


def add_swagger_doc():
    AuthenticateEndpoint.decorators.extend([
        doc.summary("Authenticate user and get token"),
        doc.consumes(LoginSwDoc, location='body'),
        doc.produces(LoginSwDoc),
    ])

    RetrieveUserEndpoint.decorators.extend([
        doc.summary("Retrieve use logged in"),
        doc.consumes({'AUTHORIZATION': str}, location='header'),
    ])

    VerifyEndpoint.decorators = [
        protected(),
        doc.summary("Verify token"),
        doc.consumes({'Authorization': str}, location='header'),
    ]

    RefreshEndpoint.decorators.extend([
        doc.summary("refresh token"),
        doc.consumes({'Authorization': str}, location='header'),
        doc.consumes({'refresh_token': str}, location='body'),
    ])