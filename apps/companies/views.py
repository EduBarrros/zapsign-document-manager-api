import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.response import api_response

from .serializers import CompanySerializer
from .services import CompanyService

logger = logging.getLogger(__name__)


@extend_schema(tags=["Companies"])
class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return CompanyService().get_active_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = CompanyService().create_company(
            user=request.user,
            **serializer.validated_data,
        )

        logger.info(
            "Empresa criada company_id=%s user_id=%s name=%s",
            company.id,
            request.user.id,
            company.name,
        )

        return api_response(
            data=CompanySerializer(company).data,
            status=status.HTTP_201_CREATED,
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