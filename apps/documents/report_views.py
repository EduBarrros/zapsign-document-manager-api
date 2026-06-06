import logging

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from core.response import api_response
from .repositories import DocumentRepository
from apps.signers.repositories import SignerRepository

logger = logging.getLogger(__name__)


@extend_schema(tags=["Reports"])
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
