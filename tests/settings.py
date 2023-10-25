SECRET_KEY = '1234'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_Db',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'tests.test_app',
    'rest_framework'
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
]

ROOT_URLCONF = 'tests.urls'

RESTFRAMEWORK = {
    'UNAUTHENTICATED_USER': None,
}
