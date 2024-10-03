from rest_framework import serializers
from .models import IPUsage
from subscriptions.models import Subscription
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

class IPUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPUsage
        fields = ['id', 'ip_address', 'free_sessions_used', 'last_usage_date']

class UserPackageStatusSerializer(serializers.Serializer):

    def get_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.username
        return None

    def validate(self, data):

        request = self.context.get('request')
        ip_address = self.get_client_ip(request)

        if not ip_address:
            raise serializers.ValidationError("IP address is required.")

        user = self.check_access_token(request.data.get('access_token'))

        if not user:
            # Kiểm tra người dùng chưa đăng nhập (sử dụng gói free)
            ip_usage, created = IPUsage.objects.get_or_create(ip_address=ip_address)
            if ip_usage.free_sessions_used >= 1:  # Giả sử chỉ cho phép 1 lần sử dụng miễn phí
                data['can_make_request'] = False
                data['message'] = "Bạn đã sử dụng hết lượt dùng thử miễn phí. Vui lòng đăng nhập hoặc mua gói dịch vụ."
            else:
                data['can_make_request'] = True
                data['message'] = "Bạn đang sử dụng gói dùng thử miễn phí."
                # Increment free_sessions_used
                ip_usage.free_sessions_used += 1
                ip_usage.save()
        else:
            # Kiểm tra người dùng đã đăng nhập
            
            remaining_sessions = self.get_remaining_sessions(user)

            if remaining_sessions > 0:
                data['can_make_request'] = True
                data['message'] = f"Bạn còn {remaining_sessions} lượt sử dụng."
            else:
                data['can_make_request'] = False
                data['message'] = "Bạn đã hết lượt sử dụng. Vui lòng mua thêm gói dịch vụ."
                

        return data

    def get_remaining_sessions(self, user):
        subscription = Subscription.objects.filter(user=user).first()
        if subscription:
            return subscription.remaining_sessions
        return 0

    def get_client_ip(self, request):
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            # Xử lý trường hợp có nhiều IP do proxy
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        return ip_address
    
    def check_access_token(self, access_token):
        try:
            # Decode the access token
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            exp = payload['exp']

            # Check if token has expired
            if datetime.fromtimestamp(exp) < datetime.now():
                return False

            # Get the user
            user = User.objects.get(id=user_id)
            return user
        except jwt.ExpiredSignatureError:
            # Token has expired
            return False
        except jwt.InvalidTokenError:
            # Invalid token
            return False
        except User.DoesNotExist:
            # User not found
            return False

