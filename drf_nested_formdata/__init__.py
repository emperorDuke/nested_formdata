__title__ = 'drf_nested_formdata'
__version__ = '0.1.4'
__author__ = 'Duke Effiom'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020'

# Version synonym
VERSION = __version__

from .utils import NestedFormDataSerializer
from .mixins import UtilityMixin
from .parser import NestedMultpartParser