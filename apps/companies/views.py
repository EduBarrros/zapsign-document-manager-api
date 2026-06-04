from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Companies"])
class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(deleted_at__isnull=True)

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()
        company.deleted_at = timezone.now()
        company.save()
        return Response(status=status.HTTP_204_NO_CONTENT)