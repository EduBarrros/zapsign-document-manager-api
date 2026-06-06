from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer
from drf_spectacular.utils import extend_schema
from .services import CompanyService

@extend_schema(tags=["Companies"])
class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(
        user=self.request.user,
        deleted_at__isnull=True
    )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()
        CompanyService.soft_delete(company)
        return Response(status=status.HTTP_204_NO_CONTENT)