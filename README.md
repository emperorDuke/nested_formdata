DRF NESTED FORMDATA
===================

A library that parses nested json or form data to python object.

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/emperorDuke/nested_formdata)](https://github.com/emperorDuke/nested_formdata/releases)
[![PyPI - License](https://img.shields.io/pypi/l/drf_nested_formdata)](https://pypi.python.org/pypi/drf-nested-formdata)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drf_nested_formdata)](https://pypi.python.org/pypi/drf-nested-formdata)
[![PyPI](https://img.shields.io/pypi/v/drf_nested_formdata)](https://pypi.python.org/pypi/drf-nested-formdata)

Overview
========
SPA's, sometimes send nested form data or json as requests encoded by some javascript libraries like [json-form-data](https://github.com/hyperatom/json-form-data#readme) which can be difficult to handle due to the key naming conventions. This library helps to eliminate that difficulty, by parsing that nested requests into a more predictable python object that can be used by libraries like [drf_writable_nested](https://github.com/beda-software/drf-writable-nested#readme) or used directly in the code.


Installation
============

```
pip install drf_nested_formdata
```

Usage
=====

The utiliy class can be used directly in any part of the code.

````python

from drf_nested_formdata.utils import NestedForm

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
````
Note
----
``.is_valid()`` should be called before accessing the ``.data``

````python
form = NestedForm(data, **options)
form.is_valid(raise_exception=True)
````
The parsed result will look like below:

```python
print(form.data)

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

The parser is used with a djangorestframework view classes.

Parser classes supported:
------------------------
- ``NestedMultiPartParser``: is a default DRF multipart parser that suppport parsing nested form data.
- ``NestedJSONParser``: is a default DRF JSONParser that support parsing nested json request.

Add the parser to your django settings file

```python

#...

REST_FRAMEWORK = {
    DEFAULT_PARSER_CLASSES = [
        # nested parser are just default DRF parsers with extended 
        # functionalities to support nested 
        
        'drf_nested_formdata.parsers.NestedMultiPartParser,
        'drf_nested_formdata.parsers.NestedJSONPartParser,
        'rest_framework.parsers.FormParser',

        # so this settings will work in respective of a nested request 
        # or not
    ]
}

#...

```
To change default settings of the parsers, add ``OPTIONS`` to ``NESTED_FORM_PARSER`` with the new settings to your django settings file

```python
#..

NESTED_FORM_PARSER = {
    'OPTIONS': { 
        'allow_empty': False, 
        'allow_blank': True 
    }
}

#...

```
The parsers can also be used directly in a ``rest_framework`` view class

```python

from rest_framework.views import APIView
from rest_framework.parsers import FormParser
from rest_framework.response import Response

from drf_nested_formdata.parsers import NestedMultiPartParser, NestedJSONParser

class TestMultiPartParserView(APIView):
    parser_classes = (NestedMultiPartParser, FormParser)

    def post(self, request):
        return Response(data=request.data, status=200)
    
# or

class TestJSONParserView(APIView):
    parser_classes = (NestedJSONParser, FormParser)

    def post(self, request):
        return Response(data=request.data, status=200)

```

For example, a form or JSON data with nested params like below can be posted to any of the above drf view:

```python
data = {
    '[0][attribute]': 'true',
    '[0][verbose][0]': 'bazz',
    '[0][verbose][1]': 'foo',
    '[0][variant][vendor_metric]': 'null',
    '[0][variant][metric_verbose_name]': 'Large',
    '[0][foo][baaz]': 'false',
    '[1][attribute]': 'size',
    '[1][verbose]': '[]',
    '[1][variant][vendor_metric]': '{}',
    '[1][variant][metric_verbose_name][foo][baaz][]': 'Large',
    '[1][foo][baaz]': '',
    '[1][logo]': '235'
}
```
after being parsed, the ``request.data`` will look like this:

```python
print(request.data)

data = [
    {
        'attribute': True, 
        'verbose': ['bazz', 'foo'], 
        'variant': {
            'vendor_metric': None, 
            'metric_verbose_name': 'Large'
        }, 
        'foo': { 'baaz': False }
    }, 
    {
        'attribute': 'size', 
        'verbose': None, 
        'variant': {
            'vendor_metric': None, 
            'metric_verbose_name': { 'foo': { 'baaz': ['Large'] } }
        }, 
        'foo': { 'baaz': '' },
        'logo': 235
    }
]
```

Options
=======
Option|Default|Description
------|-------|-----------
allow_blank |``True``|shows empty string ``''`` in the object
allow_empty |``False``|shows empty ``list`` or ``dict`` object

Tests
=====
```
py runtests.py
```

Author
=======
@Copyright 2020, Duke Effiom
