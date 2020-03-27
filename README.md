DRF_NESTED_FORM_DATA
=====================

A library that converts nested json-like form data back to python object.

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/emperorDuke/nested_formdata)]()
[![PyPI - License](https://img.shields.io/pypi/l/drf_nested_formdata)](https://pypi.python.org/pypi/drf-nested-formdata)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drf_nested_formdata)](https://pypi.python.org/pypi/drf-nested-formdata)
[![PyPI](https://img.shields.io/pypi/v/drf_nested_formdata)](https://pypi.python.org/pypi/drf-nested-formdata)

Overview
========
SPA's, sometimes send nested form data or json as requests which can be difficult to handle due to the key naming conventions. This library helps to eliminate that difficulty, by parsing that nested request into python object that can be used by libraries like ``drf_writable_nested``.

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

The utiliy class can be used directly in any part of the code.

````python

from drf_nested_formdata.utils import NestedFormDataSerializer

data = {
    'item[attribute][0][user_type]': 'size',
    'item[attribute][1][user_type]': '',
    'item[verbose][]': '',
    'item[variant][vendor_metric]': '[]',
    'item[variant][metric_verbose_name]': 'Large',
    'item[foo][baaz]': 'null',
}

options = {
    'allow_blank': True,
    'allow_empty': False
}

serializerObject = NestedFormDataSerializer(data, **options)
serializerObject.is_valid(raise_exception=True)
````
The parsed result will look like below:

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
            'vendor_metric': None, 
            'metric_verbose_name': 'Large'
        }, 
        'foo': { 'baaz': None }
    }
}
```
DRF Integration
===============

The parser is used with a djangorestframework view class.

Parser classes supported:
------------------------
- ``NestedMultipartParser``: which is used for parsing nested form data.
- ``NestedJSONParser``: which is used for parsing nested json request.

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

Form example, a form data with nested params like below can be posted to the above drf view:

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

Options
=======
Option|Default|Description
------|-------|-----------
allow_blank|``True``|shows empty string ``''``in the object
allow_empty|``False``|shows empty ``list`` or ``dict`` object

Note
----
``.is_valid()`` should be called before accessing the ``.data``


Author
=======
2020, EmperorDuke
