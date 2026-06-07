import logging

from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.views import APIView

from core.response import api_response
from .repositories import DocumentRepository
from apps.signers.repositories import SignerRepository

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["Reports"],
    summary="Relatório geral",
    description=(
        "Retorna um resumo de documentos e signatários do usuário autenticado, "
        "agrupados por status. Considera apenas registros ativos (não deletados)."
    ),
    examples=[
        OpenApiExample(
            "Relatório com dados",
            value={
                "data": {
                    "documents": {
                        "total": 42,
                        "by_status": {"pending": 20, "signed": 18, "cancelled": 4},
                    },
                    "signers": {
                        "total": 87,
                        "by_status": {"pending": 30, "signed": 50, "rejected": 7},
                    },
                },
                "error": None,
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            "Usuário sem dados",
            value={
                "data": {
                    "documents": {"total": 0, "by_status": {}},
                    "signers": {"total": 0, "by_status": {}},
                },
                "error": None,
            },
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
class ReportView(APIView):
    def __init__(self, *args, document_repository=None, signer_repository=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_repository = document_repository or DocumentRepository()
        self.signer_repository = signer_repository or SignerRepository()

    def get(self, request):
        data = {
            'documents': self.document_repository.get_summary_for_user(request.user),
            'signers': self.signer_repository.get_summary_for_user(request.user),
        }

        logger.info('Relatório gerado user_id=%s', request.user.id)

        return api_response(data=data)
