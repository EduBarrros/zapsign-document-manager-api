import logging

from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from core.response import api_response
from .models import Signer
from .serializers import SignerRequestSerializer, SignerUpdateSerializer, SignerResponseSerializer
from .services import SignerService
from .repositories import SignerRepository
from apps.documents.repositories import DocumentRepository

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
@extend_schema(
    methods=["POST"],
    summary="Adicionar signatário",
    description="Adiciona um signatário a um documento existente do usuário autenticado.",
    examples=[
        OpenApiExample(
            "Payload de criação",
            value={"name": "Maria Souza", "email": "maria@email.com", "document": 1},
            request_only=True,
        ),
        OpenApiExample(
            "Signatário criado",
            value={"data": _SIGNER_EXAMPLE, "error": None},
            response_only=True,
            status_codes=["201"],
        ),
        OpenApiExample(
            "Documento não encontrado",
            value={"data": None, "error": {"message": "Documento não encontrado ou sem permissão", "code": "DOCUMENT_NOT_FOUND"}},
            response_only=True,
            status_codes=["404"],
        ),
    ],
)
@extend_schema(
    methods=["PUT"],
    summary="Atualizar signatário",
    description="Substitui completamente os dados de um signatário. O campo `document` deve ser informado.",
    examples=[
        OpenApiExample(
            "Payload completo",
            value={"name": "Maria Souza Editada", "email": "maria.nova@email.com", "document": 1},
            request_only=True,
        ),
        OpenApiExample(
            "Signatário atualizado",
            value={"data": _SIGNER_EXAMPLE, "error": None},
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
@extend_schema(
    methods=["PATCH"],
    summary="Atualizar signatário parcialmente",
    description="Atualiza apenas os campos informados. Todos os campos são opcionais.",
    examples=[
        OpenApiExample(
            "Payload parcial",
            value={"name": "Maria Souza Editada"},
            request_only=True,
        ),
        OpenApiExample(
            "Signatário atualizado",
            value={"data": _SIGNER_EXAMPLE, "error": None},
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
@extend_schema(
    methods=["DELETE"],
    summary="Remover signatário",
    description="Realiza soft delete do signatário. O registro não é removido do banco, apenas marcado como deletado e excluído das listagens.",
)
class SignerViewSet(viewsets.ModelViewSet):
    serializer_class = SignerResponseSerializer

    def __init__(self, *args, signer_repository=None, document_repository=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.signer_repository = signer_repository or SignerRepository()
        self.document_repository = document_repository or DocumentRepository()

    def get_serializer_class(self):
        if self.action == 'create':
            return SignerRequestSerializer
        if self.action in ('update', 'partial_update'):
            return SignerUpdateSerializer
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document_id = serializer.validated_data['document']
        document_qs = self.document_repository.get_active_for_user(request.user).filter(id=document_id)
        if not document_qs.exists():
            return api_response(
                error='Documento não encontrado ou sem permissão',
                error_code='DOCUMENT_NOT_FOUND',
                status=status.HTTP_404_NOT_FOUND,
            )

        document = document_qs.first()
        email = serializer.validated_data['email']

        if self.signer_repository.exists_for_document(document, email):
            return api_response(
                error='Já existe um signatário com este email neste documento',
                error_code='SIGNER_ALREADY_EXISTS',
                status=status.HTTP_409_CONFLICT,
            )

        signer = Signer.objects.create(
            name=serializer.validated_data['name'],
            email=email,
            document=document,
        )

        logger.info(
            'Signatário criado signer_id=%s document_id=%s user_id=%s',
            signer.id,
            document.id,
            request.user.id,
        )

        return api_response(
            data=SignerResponseSerializer(signer).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        signer = self.get_object()
        serializer = self.get_serializer(signer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(
            'Signatário atualizado signer_id=%s document_id=%s user_id=%s',
            signer.id,
            signer.document_id,
            request.user.id,
        )

        return api_response(data=SignerResponseSerializer(signer).data)

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
