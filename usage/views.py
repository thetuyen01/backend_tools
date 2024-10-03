# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from sessions_usage.models import SessionUsage
from .models import IPUsage
from .serializers import IPUsageSerializer

class UseFreePackageView(APIView):
    def post(self, request):
        ip_address = request.META.get('REMOTE_ADDR')  # Lấy địa chỉ IP của người dùng
        ip_usage, created = IPUsage.objects.get_or_create(ip_address=ip_address)

        # Kiểm tra xem người dùng có đăng nhập không
        user = request.user if request.user.is_authenticated else None

        if ip_usage.free_usage_count < 1:  # Giới hạn chỉ cho phép sử dụng một lần
            # Tăng số lần sử dụng gói miễn phí
            ip_usage.free_usage_count += 1
            ip_usage.last_usage_date = timezone.now()
            ip_usage.save()

            # Lưu thông tin vào SessionUsage
            session_usage = SessionUsage.objects.create(
                user=user,  # Nếu người dùng chưa đăng nhập, giá trị sẽ là None
                ip_usage=ip_usage,  # Liên kết với đối tượng IPUsage
                used_sessions=1,
                usage_date=timezone.now()
            )
            return Response({'message': 'Bạn đã sử dụng gói miễn phí thành công!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Bạn đã sử dụng gói miễn phí một lần từ địa chỉ IP này. Vui lòng đăng nhập để mua gói dịch vụ khác.'},
                status=status.HTTP_403_FORBIDDEN
            )

class CheckUserPackageStatusView(APIView):
    def get(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        serializer = UserPackageStatusSerializer(data={'ip_address': ip_address}, context={'request': request})
        
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

