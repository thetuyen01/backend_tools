from rest_framework import serializers
from .models import Package, Subscription, DetailPackage

class DetailPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailPackage
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()   
    class Meta:
        model = Package
        fields = ['id', 'name', 'price', 'sessions', 'duration', 'details']
    def get_details(self, obj):
        return DetailPackageSerializer(obj.detailpackage_set.all(), many=True).data

    


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

