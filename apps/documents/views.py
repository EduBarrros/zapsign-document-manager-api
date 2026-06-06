import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from core.response import api_response
from .serializers import (
    DocumentResponseSerializer,
    DocumentCreateSerializer
)
from .services import DocumentService
from .repositories import DocumentRepository

logger = logging.getLogger(__name__)


@extend_schema(tags=["Documents"])
@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter("status", OpenApiTypes.STR, description="Filtrar por status (pending, signed, cancelled)"),
        OpenApiParameter("company", OpenApiTypes.INT, description="Filtrar por ID da empresa"),
    ],
)
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentResponseSerializer

    def __init__(self, *args, document_repository=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_repository = document_repository or DocumentRepository()

    def get_queryset(self):
        qs = self.document_repository.get_active_for_user(self.request.user)
        status = self.request.query_params.get('status')
        company_id = self.request.query_params.get('company')
        if status:
            qs = qs.filter(status=status)
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentResponseSerializer

    def create(self, request, *args, **kwargs):
        serializer = DocumentCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        company = serializer.validated_data['company']

        service = DocumentService()

        try:
            document = service.create_document_with_signers(
                data=dict(serializer.validated_data),
                company=company,
            )

            return api_response(
                data=DocumentResponseSerializer(document).data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as exception:
            logger.error(
                'Erro ao criar documento user_id=%s company_id=%s name=%s',
                request.user.id,
                company.id,
                serializer.validated_data.get('name'),
                exc_info=True,
            )
            return api_response(
                error=str(exception),
                error_code='ZAPSIGN_ERROR',
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @extend_schema(
        methods=["POST"],
        request=None,
        responses={200: DocumentResponseSerializer},
        summary="Re-executa a análise de IA sobre o conteúdo do documento.",
    )
    @action(detail=True, methods=["post"], url_path="analyze")
    def analyze(self, request, pk=None):
        document = self.get_object()
        document = DocumentService().reanalyze_document(document)
        return api_response(data=DocumentResponseSerializer(document).data)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()

        logger.info(
            'Requisição de exclusão de documento document_id=%s user_id=%s',
            document.id,
            request.user.id,
        )

        service = DocumentService()
        service.delete_document(document)

        return Response(status=status.HTTP_204_NO_CONTENT)
