from rest_framework.parsers import MultiPartParser, JSONParser

from .utils import NestedForm
from .settings import api_settings


class NestedMultiPartParser(MultiPartParser):
    """
    Parser for multipart form data that is nested and also
    it may include files
    """
    options = api_settings.NESTED_PARSER_OPTIONS

    def parse(self, stream, media_type=None, parser_context=None):
        parsed = super().parse(stream, media_type, parser_context)

        # files and data have to be merged into one
        if parsed.files:
            self._full_data = parsed.data.copy()
            self._full_data.update(parsed.files)
        else:
            self._full_data = parsed.data

        form = NestedForm(self._full_data, **self.options)

        if form.is_valid():
            return form.data
        
        return parsed


class NestedJSONParser(JSONParser):
    """
    Parser for JSON data that is nested
    """
    options = api_settings.NESTED_PARSER_OPTIONS

    def parse(self, stream, media_type=None, parser_context=None):
        parsed = super().parse(stream, media_type, parser_context)

        form = NestedForm(parsed, **self.options)

        if form.is_valid():
            return form.data
        
        return parsed

