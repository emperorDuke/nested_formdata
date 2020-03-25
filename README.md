DRF NESTED FORM-DATA
=====================
[![Build Status](https://travis-ci.org/beda-software/drf-writable-nested.svg?branch=master)](https://travis-ci.org/beda-software/drf-writable-nested)
[![codecov](https://codecov.io/gh/beda-software/drf-writable-nested/branch/master/graph/badge.svg)](https://codecov.io/gh/beda-software/drf-writable-nested)
[![pypi](https://img.shields.io/pypi/v/drf-writable-nested.svg)](https://pypi.python.org/pypi/drf-nested-formdata)
[![pyversions](https://img.shields.io/pypi/pyversions/drf-writable-nested.svg)](https://pypi.python.org/pypi/drf-nested-formdata)

This is a nested multipart parser for Django REST Framework which parses
nested form-data into its primitive data structure.

Requirements
============

- Python (2.7, 3.5, 3.6, 3.7)
- Django (1.9, 1.10, 1.11, 2.0, 2.1, 2.2)
- djangorestframework (3.5+)

Installation
============

```
pip install drf-writable-nested
```

Usage
=====

For example, for the following model structure:

```python

from rest_framework.views import APIView
from rest_framework.parsers import FormParser
from rest_framework.response import Response

from drf_nested_formdata.parser import NestedMultpartParser

class TestView(APIView):
    parser_classes = (NestedMultpartParser, FormParser)

    def post(self, request):

        return Response(data=request.data, status=200)

```

For example, we can post a nested data like below to this view:

```python
data = {
    '[0][attribute]': 'size',
    '[0][verbose][0]': 'bazz',
    '[0][verbose][1]': 'foo',
    '[0][variant][vendor_metric]': '456',
    '[0][variant][metric_verbose_name]': 'Large',
    '[0][foo][baaz]': 'ggg',
    '[1][attribute]': 'size',
    '[1][verbose]': 'size',
    '[1][variant][vendor_metric]': 'L',
    '[1][variant][metric_verbose_name][foo][baaz][]': 'Large',
    '[1][foo][baaz]': 'true'
}
```
Our parsed request.data should look like this:

```python
print(request.data)
```
```python
data = [
    {
        'attribute': 'size', 
        'verbose': ['bazz', 'foo'], 
        'variant': {
            'vendor_metric': 456, 
            'metric_verbose_name': 'Large'
            }, 
        'foo': { 'baaz': 'ggg' }
    }, 
    {
        'attribute': 'size', 
        'verbose': 'size', 
        'variant': {
            'vendor_metric': 'L', 
            'metric_verbose_name': {
                'foo': {
                    'baaz': ['Large']
                    }
                }
            }, 
        'foo': { 'baaz': True }
    }
]
```


Authors
=======
2020, EmperorDuke
