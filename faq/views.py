from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Faq
from .serializer import FAQSerializer

class FAQView(APIView):
    def get(self, request):
        faqs = Faq.objects.all()
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data)