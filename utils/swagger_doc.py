from sanic_openapi import doc


class UserSwDoc:
    username = doc.String("Username", required=True)
    password = doc.String("Password", required=True)
    full_name = doc.String("User full name", required=True)


class LoginSwDoc:
    username = doc.String("Username", required=True)
    password = doc.String("Password", required=True)


class TweetSwDoc:
    msg = doc.String("meg that user want to share", required=True)
    tags = doc.List(str, description="List tag", required=True)
