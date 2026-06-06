import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import CompanySerializer
from .services import CompanyService

logger = logging.getLogger(__name__)


@extend_schema(tags=["Companies"])
class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return CompanyService().get_active_for_user(self.request.user)

    def perform_create(self, serializer):
        company = CompanyService().create_company(
            user=self.request.user,
            **serializer.validated_data,
        )

        logger.info(
            "Empresa criada company_id=%s user_id=%s name=%s",
            company.id,
            self.request.user.id,
            company.name,
        )

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()

        CompanyService().soft_delete(company)

        logger.info(
            "Soft delete de empresa company_id=%s user_id=%s",
            company.id,
            request.user.id,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)