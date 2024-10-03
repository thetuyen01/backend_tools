from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, CustomTokenRefreshSerializer
from .backends import PhoneOrEmailAuthenticationBackend
from django.contrib.auth import login
from .serializers import LoginSerializer

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from .models import User
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
import jwt
from datetime import datetime

# Create your views here.
class SignUpView(APIView):
    
    def post(self,request):
        try:
            data = request.data 
            serializer = RegisterSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    "message":serializer.errors,
                    "status":False
                },status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()

            return Response({
                "message":"successful registration",
                "status": True
            },status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": False,
                "code": 500
            })

class LoginView(APIView):

    def post(self, request):
        try:
            data = request.data 
            if data.get('isGoogle'):
                return self.login_with_google(request, data.get('token'))
            
            serializer = LoginSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    "message": serializer.errors,
                    "status": False
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = PhoneOrEmailAuthenticationBackend().authenticate(request, phone_or_email=serializer.data['phone_or_email'], password=serializer.data['password'])
            if not user:
                return Response({
                    "status": False,
                    "message": "account password wrong"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            login(request, user, backend='authencations.backends.PhoneOrEmailAuthenticationBackend')
            try:
                response_token = serializer.get_user_and_jwt_token(user, request=request)
                return Response(response_token, status=status.HTTP_200_OK)
            except Exception as token_error:
                return Response({
                    "status": False,
                    "message": "Token generation failed",
                    "detail": str(token_error)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e),
                "code": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def login_with_google(self, request, access_token):
        if not access_token:
            return Response({"message": "Access token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            decoded_token = auth.verify_id_token(access_token)
            is_valid_email = decoded_token.get('email_verified', False)
            email = decoded_token.get('email')
            phone = decoded_token.get('uid')

            if not is_valid_email or not email:
                return Response({"message": "Please verify your email"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create(email=email, phone=phone)

            login(request, user, backend='authencations.backends.PhoneOrEmailAuthenticationBackend')
            serializer = LoginSerializer()
            response_token = serializer.get_user_and_jwt_token(user, request=request)
            return Response(response_token, status=status.HTTP_200_OK)
        
        except auth.InvalidIdTokenError:
            return Response({"message": "Invalid ID token"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckActivatedAccountAPIView(APIView):
    def post(self, request):
        accessToken = request.data.get('accessToken')
        try:
            decoded_token = auth.verify_id_token(accessToken)
            phone_number = decoded_token.get('phone_number')
            if phone_number:
                user = User.objects.filter(phone=phone_number).first()
                if user:
                    user.is_active = True
                    user.save()
                    return Response({"message": "activated account success"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "phone_number not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        except auth.InvalidIdTokenError:
            return Response({"error": "Invalid ID token"}, status=status.HTTP_401_UNAUTHORIZED)



    def post(self, request):
        refresh_token = request.data['refresh_token']
        
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify the refresh token
            try:
                token = RefreshToken(refresh_token)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            # Check if the token has expired
            if token.check_exp():
                return Response({"error": "Refresh token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
            # Get the user from the token
            user_id = token.payload.get('user_id')
            user = User.objects.filter(id=user_id).first()
            
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if the token is blacklisted
            jti = token.payload.get('jti')
            if token.blacklist():
                return Response({"error": "Token is blacklisted"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Token is valid
            return Response({
                "message": "Refresh token is valid",
                "email": user.email,
                "isPremium": user.is_premium
            }, status=status.HTTP_200_OK)
        
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckRefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode token mà không verify để lấy payload
            payload = jwt.decode(refresh_token, options={"verify_signature": False})
            
            # Lấy thời gian hết hạn từ payload
            exp = payload.get('exp')
            
            if not exp:
                return Response({"is_valid": False}, status=status.HTTP_400_BAD_REQUEST)
            
            # Chuyển đổi thời gian hết hạn thành datetime và so sánh với thời gian hiện tại
            is_valid = datetime.fromtimestamp(exp) > datetime.now()

            return Response({"is_valid": is_valid}, status=status.HTTP_200_OK)

        except jwt.DecodeError:
            return Response({"is_valid": False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        