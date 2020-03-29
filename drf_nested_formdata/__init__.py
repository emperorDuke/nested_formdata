__title__ = 'drf_nested_formdata'
__version__ = '0.1.6'
__author__ = 'Duke Effiom'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020'

# Version synonym
from .exceptions import ParseError
from .parsers import NestedMultiPartParser, NestedJSONParser
from .mixins import UtilityMixin
from .utils import NestedForm
VERSION = __version__
