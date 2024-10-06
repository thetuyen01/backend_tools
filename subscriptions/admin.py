from django.contrib import admin

# Register your models here.
from .models import Package, DetailPackage, Subscription

admin.site.register(Package)
admin.site.register(DetailPackage)
admin.site.register(Subscription)