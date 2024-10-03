from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[RegexValidator(r'^\S+@\S+\.\S+$', "Email already exists or email is not blank")])
    username = serializers.CharField(validators=[RegexValidator(r'^\S+$', "Username already exists or username is not blank")])
    phone = serializers.CharField(validators=[RegexValidator(r'^\S+$', "Phone already exists or phone is not blank")])
    password = serializers.CharField()

    def validate(self, data):
        if data:

            if User.objects.filter(phone = data['phone']).first():
                raise serializers.ValidationError("Phone already exists or phone is not blank")
            
            if  User.objects.filter(email = data['email']).first():
                raise serializers.ValidationError("Email already exists or email is not blank")
            
            if User.objects.filter(username = data['username']).first():
                raise serializers.ValidationError("Username already exists or username is not blank")
            

            if len(data['password']) < 8:
                raise serializers.ValidationError("Password must be more than 8 characters")
            
            return data
        
    def create(self, validated_data):
        user = User.objects.create(email = validated_data['email'], username = validated_data['username'], phone = validated_data['phone'])
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()
        return user
    

class LoginSerializer(serializers.Serializer):
    
    def get_user_and_jwt_token(self, user, request):
        try:
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'isPremium': user.is_premium,  
                'status': True
            }
        except Exception as e:

            return {
                'status': False,
                'error': "An unexpected error occurred. Please try again later."
            }


    
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = RefreshToken(attrs['refresh'])
        
        # Add isPremium status to the response
        data['isPremium'] = refresh.is_premium

        return data



class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model  = User
            fields = ['phone', 'email', 'username']
