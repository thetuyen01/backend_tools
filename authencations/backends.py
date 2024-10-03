from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class PhoneOrEmailAuthenticationBackend(BaseBackend):
    def authenticate(self, request, phone_or_email=None, password=None):
        UserModel = get_user_model()
        try:
            # Tìm người dùng dựa vào số điện thoại hoặc email
            user = UserModel.objects.get(Q(phone = phone_or_email) | Q(email = phone_or_email))
            # Kiểm tra mật khẩu
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Trả về None nếu không tìm thấy người dùng
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_active and user_obj.is_staff

    def has_module_perms(self, user_obj, app_label):
        return user_obj.is_active and user_obj.is_staff
