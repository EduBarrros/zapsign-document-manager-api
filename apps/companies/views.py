import logging

from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import CompanySerializer
from drf_spectacular.utils import extend_schema
from .services import CompanyService
from .repositories import CompanyRepository

logger = logging.getLogger(__name__)


@extend_schema(tags=["Companies"])
class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer

    def __init__(self, *args, company_repository=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_repository = company_repository or CompanyRepository()

    def get_queryset(self):
        return self.company_repository.get_active_for_user(self.request.user)

    def perform_create(self, serializer):
        company = serializer.save(user=self.request.user)
        logger.info(
            'Empresa criada company_id=%s user_id=%s name=%s',
            company.id,
            self.request.user.id,
            company.name,
        )

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()
        logger.info(
            'Soft delete de empresa company_id=%s user_id=%s',
            company.id,
            request.user.id,
        )
        CompanyService().soft_delete(company)
        return Response(status=status.HTTP_204_NO_CONTENT)
