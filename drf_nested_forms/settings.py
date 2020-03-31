from django.conf import settings
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, 'NESTED_FORM_PARSER', {})

DEFAULTS = {
    'OPTIONS': {
        'allow_empty': False,
        'allow_blank': True
    }
}

api_settings = APISettings(USER_SETTINGS, DEFAULTS)
