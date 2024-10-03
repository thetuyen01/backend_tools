from django.db import models
from django.conf import settings

# Create your models here.
class SessionUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='session_usages')  # Khóa ngoại tới bảng `User`
    used_sessions = models.PositiveIntegerField()  # Số phiên đã sử dụng
    usage_date = models.DateTimeField(auto_now_add=True)  # Ngày sử dụng phiên

    def __str__(self):
        return f"{self.user.email} - {self.used_sessions} sessions on {self.usage_date}"
