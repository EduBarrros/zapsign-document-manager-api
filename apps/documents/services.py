import logging

from django.db import transaction

from apps.integrations.ai_analysis import GeminiClient
from apps.integrations.pdf_extractor import PDFExtractor
from apps.integrations.zapsign import ZapSignClient
from apps.signers.repositories import SignerRepository

from .models import Document
from .repositories import DocumentRepository

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository | None = None,
        signer_repository: SignerRepository | None = None,
    ):
        self.document_repository = document_repository or DocumentRepository()
        self.signer_repository = signer_repository or SignerRepository()

    def create_document_with_signers(self, data: dict, company) -> Document:
        signers_data = data.pop('signers', [])
        url_pdf = data.pop('url_pdf', None)

        logger.info(
            'Iniciando criação de documento name=%s company_id=%s signers_count=%s',
            data['name'],
            company.id,
            len(signers_data),
        )

        try:
            document_content = PDFExtractor.extract_from_url(url_pdf)
        except Exception:
            logger.warning(
                'Falha ao extrair texto do PDF url=%s company_id=%s; usando conteúdo fallback',
                url_pdf,
                company.id,
                exc_info=True,
            )
            document_content = f"""
            Nome do documento: {data['name']}
            Empresa: {company.name}
            """

        with transaction.atomic():
            document = self.document_repository.create(
                name=data['name'],
                created_by=data['created_by'],
                company=company,
                url_pdf=url_pdf,
                extracted_text=document_content
            )

            client = ZapSignClient(api_token=company.api_token)

            zapsign_create_document_response = client.create_document(
                name=document.name,
                url_pdf=document.url_pdf,
                signers=signers_data
            )

            self.document_repository.update_zapsign_fields(
                document,
                token=zapsign_create_document_response['token'],
                open_id=zapsign_create_document_response['open_id'],
                external_id=zapsign_create_document_response['external_id'],
                status=zapsign_create_document_response['status'],
            )

            document_signers = zapsign_create_document_response.get('signers', [])

            for signer_data, zapsign_signer in zip(signers_data, document_signers):
                self.signer_repository.create_for_document(
                    document,
                    name=signer_data['name'],
                    email=signer_data['email'],
                    token=zapsign_signer.get('token'),
                    external_id=zapsign_signer.get('external_id'),
                    status=zapsign_signer.get('status', 'pending'),
                    sign_url=zapsign_signer.get('sign_url'),
                )

        logger.info(
            'Documento criado document_id=%s company_id=%s zapsign_token=%s',
            document.id,
            company.id,
            document.token,
        )

        self._analyze_document_with_ai(document)
        return document

    def _analyze_document_with_ai(self, document: Document) -> None:
        logger.info('Iniciando análise de IA document_id=%s', document.id)

        try:
            gemini = GeminiClient()

            analysis_result = gemini.analyze_document(
                document_content=document.extracted_text
            )

            self.document_repository.update_ai_analysis(
                document,
                summary=analysis_result.get('summary', ''),
                missing_topics=analysis_result.get('missing_topics', []),
                insights=analysis_result.get('insights', ''),
            )

            logger.info('Análise de IA concluída document_id=%s', document.id)

        except Exception:
            logger.error(
                'Falha na análise de IA document_id=%s',
                document.id,
                exc_info=True,
            )
            self.document_repository.update_ai_analysis(
                document,
                summary='Analysis unavailable',
                missing_topics=[],
                insights='Analysis unavailable',
            )

    def delete_document(self, document: Document) -> None:
        logger.info(
            'Soft delete de documento document_id=%s company_id=%s',
            document.id,
            document.company_id,
        )
        self.signer_repository.soft_delete_by_document(document)
        self.document_repository.soft_delete(document)
