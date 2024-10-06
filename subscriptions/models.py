from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Package(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sessions = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(help_text="Duration in days")

    def __str__(self):
        return self.name

class DetailPackage(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    detail = models.CharField(max_length=50)

    def __str__(self):
        return self.package.name + " - " + self.detail

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')  # Khóa ngoại tới bảng `User`
    package = models.ForeignKey(Package, on_delete=models.CASCADE) # Khóa ngoại tới bảng `Package`
    remaining_sessions = models.PositiveIntegerField(default=0)  # Số phiên còn lại trong gói
    purchase_date = models.DateTimeField(auto_now_add=True)  # Ngày mua gói

    def __str__(self):
        return f"{self.user.email} - {self.package.name}"