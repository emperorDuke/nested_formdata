__title__ = 'drf_nested_formdata'
__version__ = '1.1.3'
__author__ = 'Duke Effiom'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021'

# Version synonym
from .exceptions import ParseException
from .parsers import NestedMultiPartParser, NestedJSONParser
from .mixins import UtilityMixin
from .utils import NestedForms

VERSION = __version__
