from django.urls import re_path
from .views import TestView

urlpatterns = [
    re_path(r'^test/$', TestView.as_view(), name='test_view'),
]