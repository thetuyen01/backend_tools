from django.db import models

# Create your models here.
class IPUsage(models.Model):
    ip_address = models.GenericIPAddressField(primary_key=True)  # Địa chỉ IP
    free_sessions_used = models.PositiveIntegerField(default=0)  # Số lần đã sử dụng miễn phí
    last_usage_date = models.DateTimeField(auto_now=True)  # Ngày sử dụng phiên miễn phí gần nhất

    def __str__(self):
        return f"{self.ip_address} - {self.free_sessions_used} free sessions"
