from rest_framework.parsers import MultiPartParser

from .utils import NestedFormDataSerializer


class NestedMultpartParser(MultiPartParser):
    """
    Parser for multipart form data that is nested and also
    it may include files
    """
    def parse(self, stream, media_type=None, parser_context=None):
        parsed = super().parse(stream, media_type, parser_context)

        # files and data have to be merged into one
        if parsed.files:
            self._full_data = parsed.data.copy()
            self._full_data.update(parsed.files)
        else:
            self._full_data = parsed.data

        serializerObject = NestedFormDataSerializer(self._full_data)

        if serializerObject.is_valid():
            return serializerObject.data
        
        return parsed
