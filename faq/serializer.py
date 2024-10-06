from rest_framework import serializers
from .models import Faq

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = '__all__'