from django.urls import re_path
from .views import TestViewMultiPart, TestViewJSON

urlpatterns = [
    re_path(r'^test-multipart/$', TestViewMultiPart.as_view(),
            name='test_multipart'),
    re_path(r'^test-json/$', TestViewJSON.as_view(), name='test_json')
]
