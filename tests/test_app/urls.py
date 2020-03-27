from django.urls import re_path
from .views import TestViewMultipart, TestViewJSON

urlpatterns = [
    re_path(r'^test-multipart/$', TestViewMultipart.as_view(), name='test_multipart'),
    re_path(r'^test-json/$', TestViewJSON.as_view(), name='test_json')
]