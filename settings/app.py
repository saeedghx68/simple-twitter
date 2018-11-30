def load_settings(app, db):
    import os
    from dotenv import load_dotenv

    print('loading setting app ...')

    load_dotenv(verbose=True)

    app.config.CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    app.config.DB_HOST = os.getenv('DB_HOST', 'localhost')
    if os.getenv('ENVIRONMENT') != 'test':
        app.config.DB_DATABASE = os.getenv('DB_DATABASE', 'twitter_db')
    else:
        app.config.DB_DATABASE = os.getenv('TEST_DB_DATABASE', 'test_twitter_db')
    app.config.DB_USER = os.getenv('DB_USER', 'saeed')
    app.config.DB_PASSWORD = os.getenv('DB_PASSWORD', '123')
    app.config.DB_PORT = os.getenv('DB_PORT', 5432)

    app.config.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    app.config.REDIS_PORT = os.getenv('REDIS_PORT', '6379')

    app.config.API_VERSION = os.getenv('API_VERSION')
    app.config.API_TITLE = os.getenv('API_TITLE')
    app.config.API_DESCRIPTION = os.getenv('API_DESCRIPTION')
    app.config.API_TERMS_OF_SERVICE = os.getenv('API_TERMS_OF_SERVICE')
    app.config.API_PRODUCES_CONTENT_TYPES = os.getenv('API_PRODUCES_CONTENT_TYPES')
    app.config.API_CONTACT_EMAIL = os.getenv('API_CONTACT_EMAIL')
    app.config.DEBUG = bool(os.getenv('DEBUG', False))
    app.config.WORKERS = os.getenv('WORKERS', 8)

    app.config.DB_CONN_STR = f'postgresql://{app.config.DB_USER}:{app.config.DB_PASSWORD}@{app.config.DB_HOST}:' \
              f'{app.config.DB_PORT}/{app.config.DB_DATABASE}'
