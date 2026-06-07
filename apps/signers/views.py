import logging

from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import SignerRequestSerializer, SignerResponseSerializer
from .services import SignerService
from .repositories import SignerRepository

logger = logging.getLogger(__name__)


_SIGNER_EXAMPLE = {
    "id": 1,
    "name": "Maria Souza",
    "email": "maria@email.com",
    "token": "signer-token-xyz",
    "external_id": "signer-ext-xyz",
    "status": "pending",
    "sign_url": "https://sandbox.app.zapsign.com.br/verificar/xyz",
}


@extend_schema(tags=["Signers"])
@extend_schema(
    methods=["GET"],
    summary="Listar signatários",
    description="Retorna todos os signatários ativos vinculados a documentos do usuário autenticado.",
    parameters=[
        OpenApiParameter("status", OpenApiTypes.STR, description="Filtrar por status: `pending`, `signed` ou `rejected`"),
        OpenApiParameter("document", OpenApiTypes.INT, description="Filtrar por ID do documento"),
    ],
    examples=[
        OpenApiExample(
            "Lista de signatários",
            value={"count": 1, "next": None, "previous": None, "results": [_SIGNER_EXAMPLE]},
            response_only=True,
        )
    ],
)
class SignerViewSet(viewsets.ModelViewSet):
    serializer_class = SignerResponseSerializer

    def __init__(self, *args, signer_repository=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.signer_repository = signer_repository or SignerRepository()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SignerRequestSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = self.signer_repository.get_active_for_user(self.request.user)
        status = self.request.query_params.get('status')
        document_id = self.request.query_params.get('document')
        if status:
            qs = qs.filter(status=status)
        if document_id:
            qs = qs.filter(document_id=document_id)
        return qs

    def perform_create(self, serializer):
        signer = serializer.save()
        logger.info(
            'Signatário criado signer_id=%s document_id=%s user_id=%s',
            signer.id,
            signer.document_id,
            self.request.user.id,
        )

    def destroy(self, request, *args, **kwargs):
        signer = self.get_object()
        logger.info(
            'Soft delete de signatário signer_id=%s document_id=%s user_id=%s',
            signer.id,
            signer.document_id,
            request.user.id,
        )
        SignerService().soft_delete(signer)
        return Response(status=status.HTTP_204_NO_CONTENT)
