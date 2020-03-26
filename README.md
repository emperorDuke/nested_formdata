DRF NESTED FORM-DATA
=====================

[![pypi](https://img.shields.io/pypi/v/drf-writable-nested.svg)](https://pypi.python.org/pypi/drf-nested-formdata)
[![pyversions](https://img.shields.io/pypi/pyversions/drf-writable-nested.svg)](https://pypi.python.org/pypi/drf-nested-formdata)

This is a nested multipart parser for Django REST Framework which parses
nested form-data into its primitive data structure. It also comes utility 
class that enables dealing with nested params in formdata anywhere in 
the code.

Requirements
============

- Python (2.7, 3.5, 3.6, 3.7)
- Django (1.9, 1.10, 1.11, 2.0, 2.1, 2.2)
- djangorestframework (3.5+)

Installation
============

```
pip install drf_nested_formdata
```

Usage
=====

The parser is used with a djangorestframework view:

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

Form example, a formdata with nested params like below can be posted to the above view:

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
The utiliy class can be used directly in any part of the code.

````python

from drf_nested_formdata.utils import NestedFormDataSerializer

data = {
    'item[attribute][0][user_type]': 'size',
    'item[attribute][1][user_type]': '',
    'item[verbose][]': '',
    'item[variant][vendor_metric]': 'L',
    'item[variant][metric_verbose_name]': 'Large',
    'item[foo][baaz]': 'null',
}

serializerObject = NestedFormDataSerializer(data)
serializerObject.is_valid(raise_exception=True)
````
The parsed result will look below:

```python
print(serializerObject.data)

data = {
    'item': {
        'attribute': [
            {'user_type': 'size'}, 
            {'user_type': ''}
        ], 
        'verbose': [''], 
        'variant': {
            'vendor_metric': 'L', 
            'metric_verbose_name': 'Large'
        }, 
        'foo': { 'baaz': None }
    }
}
```

Note
----
**.is_valid()** should be called before accessing the **.data**


Authors
=======
2020, EmperorDuke
