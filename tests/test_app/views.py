from rest_framework.views import APIView
from rest_framework.parsers import FormParser
from rest_framework.response import Response

from drf_nested_forms.parsers import NestedMultiPartParser, NestedJSONParser


class TestViewMultiPart(APIView):
    parser_classes = (NestedMultiPartParser, FormParser)

    def post(self, request):

        return Response(data=request.data, status=200)


class TestViewJSON(APIView):
    parser_classes = (NestedJSONParser, FormParser)

    def post(self, request):

        return Response(data=request.data, status=200)
