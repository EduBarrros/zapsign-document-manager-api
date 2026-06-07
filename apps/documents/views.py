import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from core.response import api_response
from .serializers import (
    DocumentResponseSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
)
from .services import DocumentService
from .repositories import DocumentRepository

logger = logging.getLogger(__name__)


_DOCUMENT_EXAMPLE = {
    "id": 1,
    "name": "Contrato de Prestação de Serviços",
    "status": "pending",
    "open_id": 98765,
    "token": "doc-token-abc123",
    "url_pdf": "https://exemplo.com/contrato.pdf",
    "external_id": "ext-abc123",
    "created_at": "2024-01-15T10:00:00Z",
    "created_by": "João Silva",
    "company": 1,
    "signers": [
        {"id": 1, "name": "Maria Souza", "email": "maria@email.com", "status": "pending", "token": "signer-token-xyz", "external_id": "signer-ext-xyz", "sign_url": "https://sandbox.app.zapsign.com.br/verificar/xyz"}
    ],
    "ai_summary": "Contrato de prestação de serviços de consultoria por 12 meses.",
    "ai_missing_topics": ["Cláusula de rescisão", "Multa por atraso"],
    "ai_insights": "O contrato não especifica prazos de pagamento.",
    "last_updated_at": "2024-01-15T10:05:00Z",
}


@extend_schema(tags=["Documents"])
@extend_schema(
    methods=["GET"],
    summary="Listar documentos",
    description="Retorna todos os documentos ativos do usuário autenticado. Inclui signatários e resultado da análise de IA.",
    parameters=[
        OpenApiParameter("status", OpenApiTypes.STR, description="Filtrar por status: `pending`, `signed` ou `cancelled`"),
        OpenApiParameter("company", OpenApiTypes.INT, description="Filtrar por ID da empresa"),
    ],
    examples=[
        OpenApiExample(
            "Lista de documentos",
            value={"count": 1, "next": None, "previous": None, "results": [_DOCUMENT_EXAMPLE]},
            response_only=True,
        )
    ],
)
@extend_schema(
    methods=["POST"],
    summary="Criar documento",
    description=(
        "Cria um documento e executa automaticamente:\n"
        "1. Extração de texto do PDF informado em `url_pdf`\n"
        "2. Envio para assinatura na ZapSign (usando o `api_token` da empresa)\n"
        "3. Análise de conteúdo com IA (resumo, insights e tópicos ausentes)\n\n"
        "Retorna `502` se a comunicação com a ZapSign falhar."
    ),
    examples=[
        OpenApiExample(
            "Payload de criação",
            value={
                "name": "Contrato de Prestação de Serviços",
                "created_by": "João Silva",
                "company": 1,
                "url_pdf": "https://exemplo.com/contrato.pdf",
                "signers": [
                    {"name": "Maria Souza", "email": "maria@email.com"}
                ],
            },
            request_only=True,
        ),
        OpenApiExample(
            "Documento criado com sucesso",
            value={"data": _DOCUMENT_EXAMPLE, "error": None},
            response_only=True,
            status_codes=["201"],
        ),
        OpenApiExample(
            "Falha na comunicação com ZapSign",
            value={"data": None, "error": {"message": "Connection timeout", "code": "ZAPSIGN_ERROR"}},
            response_only=True,
            status_codes=["502"],
        ),
    ],
)
@extend_schema(
    methods=["PUT"],
    summary="Atualizar documento",
    description="Substitui completamente os dados do documento. Não reprocessa a ZapSign nem a análise de IA — use `POST /{id}/analyze/` para re-analisar.",
    examples=[
        OpenApiExample(
            "Payload completo",
            value={
                "name": "Contrato Atualizado",
                "created_by": "João Silva",
                "company": 1,
                "url_pdf": "https://exemplo.com/contrato-v2.pdf",
                "signers": [{"name": "Maria Souza", "email": "maria@email.com"}],
            },
            request_only=True,
        ),
        OpenApiExample(
            "Documento atualizado",
            value={"data": _DOCUMENT_EXAMPLE, "error": None},
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
@extend_schema(
    methods=["PATCH"],
    summary="Atualizar documento parcialmente",
    description="Atualiza apenas os campos informados. Útil para corrigir o nome ou `created_by` sem reprocessar tudo.",
    examples=[
        OpenApiExample(
            "Apenas nome",
            value={"name": "Contrato Corrigido"},
            request_only=True,
        ),
        OpenApiExample(
            "Documento atualizado",
            value={"data": _DOCUMENT_EXAMPLE, "error": None},
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
@extend_schema(
    methods=["DELETE"],
    summary="Remover documento",
    description="Realiza soft delete do documento e de todos os seus signatários. O registro permanece no banco mas é excluído das listagens.",
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
        if self.action in ('update', 'partial_update'):
            return DocumentUpdateSerializer
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
        summary="Re-executar análise de IA",
        description="Re-executa a análise Gemini sobre o texto já extraído do documento. Útil após correções ou quando a análise inicial falhou.",
        examples=[
            OpenApiExample(
                "Documento re-analisado",
                value={"data": _DOCUMENT_EXAMPLE, "error": None},
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    @action(detail=True, methods=["post"], url_path="analyze")
    def analyze(self, request, pk=None):
        document = self.get_object()
        document = DocumentService().reanalyze_document(document)
        return api_response(data=DocumentResponseSerializer(document).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        document = self.get_object()
        serializer = self.get_serializer(document, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(
            'Documento atualizado document_id=%s user_id=%s',
            document.id,
            request.user.id,
        )

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
