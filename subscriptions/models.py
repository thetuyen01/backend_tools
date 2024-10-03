from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.
class Subscription(models.Model):
    PACKAGE_CHOICES = [
        ('20-sessions', '20 Sessions'),
        ('50-sessions', '50 Sessions'),
        ('100-sessions', '100 Sessions'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')  # Khóa ngoại tới bảng `User`
    package_type = models.CharField(max_length=50, choices=PACKAGE_CHOICES)  # Loại gói
    remaining_sessions = models.PositiveIntegerField(default=0)  # Số phiên còn lại trong gói
    purchase_date = models.DateTimeField(auto_now_add=True)  # Ngày mua gói

    def __str__(self):
        return f"{self.user.email} - {self.package_type}"
