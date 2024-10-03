from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from usage.serializers import UserPackageStatusSerializer

class VoiceApiView(APIView):
    def post(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        access_token = request.data.get('access_token')
        serializer = UserPackageStatusSerializer(data={'ip_address': ip_address}, context={'request': request, 'access_token': access_token})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

