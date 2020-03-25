from rest_framework.views import APIView
from rest_framework.parsers import FormParser
from rest_framework.response import Response

from ...drf_nested_formdata.parser import NestedMultpartParser

class TestView(APIView):
    parser_classes = (NestedMultpartParser, FormParser)

    def post(self, request):

        return Response(data=request.data, status=200)

