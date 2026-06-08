import logging
from django.db import transaction
from apps.integrations.ai_analysis import GeminiClient
from apps.integrations.pdf_extractor import PDFExtractor
from apps.integrations.webhook_dispatcher import WebhookDispatcher
from apps.integrations.zapsign import ZapSignClient
from .models import Document
from .repositories import DocumentRepository
from apps.signers.repositories import SignerRepository

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
        signers_data = data.pop("signers", [])
        url_pdf = data.pop("url_pdf", None)

        logger.info(
            "Iniciando criação de documento name=%s company_id=%s signers=%s",
            data.get("name"),
            company.id,
            len(signers_data),
        )

        with transaction.atomic():
            document = self._create_document(data, company, url_pdf)

            extracted_text = self._extract_pdf(url_pdf, document, company)

            zapsign_signers = self._send_to_zapsign(document, signers_data, company)

            self._create_signers(document, signers_data, zapsign_signers)

        # _extract_pdf e _analyze_ai são chamadas síncronas intencionalmente nesta versão.
        # Em produção com volume real, ambas devem ser movidas para tasks assíncronas
        # (ex: Celery) que recebem apenas document.id — a separação por service/repository
        # já garante que a migração não exige mudanças nas camadas superiores.
        self._analyze_ai(document, extracted_text)

        WebhookDispatcher().dispatch(
            'document.created',
            {'document_id': document.id, 'company_id': company.id, 'status': document.status},
        )

        logger.info(
            "Documento criado document_id=%s company_id=%s",
            document.id,
            company.id,
        )

        return document

    def reanalyze_document(self, document: Document) -> Document:
        logger.info("Re-análise de IA iniciada document_id=%s", document.id)
        extracted_text = document.extracted_text or f"Documento - {document.name}"
        self._analyze_ai(document, extracted_text)
        return document

    def process_zapsign_webhook(self, payload: dict) -> Document | None:
        document_token = payload.get("token")
        document = self.document_repository.get_by_token(document_token)

        if not document:
            logger.warning("Webhook ZapSign: documento não encontrado token=%s", document_token)
            return None

        new_status = payload.get("status", document.status)
        self.document_repository.update_status(document, new_status)

        for signer_data in payload.get("signers", []):
            signer_token = signer_data.get("token")
            if signer_token:
                self.signer_repository.update_status_by_token(
                    signer_token,
                    status=signer_data.get("status", "pending"),
                    sign_url=signer_data.get("sign_url"),
                )

        if new_status == Document.Status.SIGNED:
            WebhookDispatcher().dispatch(
                'document.signed',
                {'document_id': document.id, 'company_id': document.company_id},
            )

        logger.info(
            "Webhook ZapSign processado document_id=%s status=%s",
            document.id,
            new_status,
        )
        return document

    def update_document(self, document: Document, **data) -> Document:
        return self.document_repository.update(document, **data)

    def delete_document(self, document: Document) -> None:
        self.document_repository.soft_delete(document)

        signers = self.signer_repository.get_active_for_document(document)
        for signer in signers:
            self.signer_repository.soft_delete(signer)

        logger.info("Soft delete de documento document_id=%s", document.id)

    def _create_document(self, data, company, url_pdf) -> Document:
        return self.document_repository.create(
            name=data["name"],
            created_by=data["created_by"],
            company=company,
            url_pdf=url_pdf,
            extracted_text="",
        )

    def _extract_pdf(self, url_pdf, document, company) -> str:
        try:
            text = PDFExtractor.extract_from_url(url_pdf)

            self.document_repository.update_extracted_text(document, text)

            logger.info("PDF processado document_id=%s", document.id)

            return text

        except Exception:
            logger.warning(
                "Falha ao extrair PDF document_id=%s url=%s",
                document.id,
                url_pdf,
                exc_info=True,
            )

            fallback = f"Documento sem extração válida - {document.name}"

            self.document_repository.update_extracted_text(document, fallback)

            return fallback

    def _send_to_zapsign(self, document, signers_data, company) -> list:
        try:
            client = ZapSignClient(api_token=company.api_token)

            response = client.create_document(
                name=document.name,
                url_pdf=document.url_pdf,
                signers=signers_data,
            )

            self.document_repository.update_zapsign_fields(
                document,
                token=response["token"],
                open_id=response["open_id"],
                external_id=response["external_id"],
                status=response["status"],
            )

            return response.get("signers", [])

        except Exception:
            logger.exception("Erro ZapSign document_id=%s", document.id)
            raise

    def _create_signers(self, document, signers_data, zapsign_signers=None):
        zapsign_signers = zapsign_signers or []
        for idx, signer in enumerate(signers_data):
            email = signer.get("email", "")
            if self.signer_repository.exists_for_document(document, email):
                logger.info(
                    "Signatário já existe, ignorando document_id=%s email=%s",
                    document.id,
                    email,
                )
                continue
            zapsign_data = zapsign_signers[idx] if idx < len(zapsign_signers) else {}
            self.signer_repository.create_for_document(
                document,
                name=signer["name"],
                email=email,
                token=zapsign_data.get("token"),
                external_id=zapsign_data.get("external_id"),
                status=zapsign_data.get("status", "pending"),
                sign_url=zapsign_data.get("sign_url"),
            )

    def _analyze_ai(self, document, extracted_text):
        try:
            gemini = GeminiClient()

            result = gemini.analyze_document(document_content=extracted_text)

            self.document_repository.update_ai_analysis(
                document,
                summary=result.get("summary", ""),
                missing_topics=result.get("missing_topics", []),
                insights=result.get("insights", ""),
            )

        except Exception:
            logger.error(
                "Falha na análise de IA document_id=%s",
                document.id,
                exc_info=True,
            )

            self.document_repository.update_ai_analysis(
                document,
                summary="Analysis unavailable",
                missing_topics=[],
                insights="",
            )