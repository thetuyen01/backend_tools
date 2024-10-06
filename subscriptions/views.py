from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Package, Subscription, DetailPackage
from .serializers import PackageSerializer, SubscriptionSerializer, DetailPackageSerializer

class PackageListView(APIView):
    def get(self, request):
        packages = Package.objects.all().prefetch_related('detailpackage_set')
        serializer = PackageSerializer(packages, many=True)

        # Nhóm các gói dịch vụ theo tên
        grouped_packages = {}
        for package in serializer.data:
            package_type = package['name'].lower().replace(' ', '_')
            if package_type not in grouped_packages:
                grouped_packages[package_type] = []
            grouped_packages[package_type].append(package)

        response = {
            'status': 'success',
            'message': 'Packages fetched successfully',
            'packages': grouped_packages
        }
        return Response(grouped_packages, status=status.HTTP_200_OK)
