SECRET_KEY = '1234'

RESTFRAMEWORK = {
    'UNAUTHENTICATED_USER': None,
}

ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

INSTALLED_APP = [
    'test.test_app'
]

