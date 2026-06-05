from django.utils import timezone
from apps.integrations.zapsign import ZapSignClient
from .models import Document
from apps.signers.models import Signer
from apps.integrations.ai_analysis import GeminiClient
from apps.integrations.pdf_extractor import PDFExtractor
from django.db import transaction

class DocumentService:
    def create_document_with_signers(self, data: dict, company) -> Document:
        signers_data = data.pop('signers', [])
        url_pdf = data.pop('url_pdf', None)

        try:
            document_content = PDFExtractor.extract_from_url(
                url_pdf
            )
        except Exception:
            document_content = f"""
            Nome do documento: {data['name']}
            Empresa: {company.name}
            """

        with transaction.atomic():
            document = Document.objects.create(
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

            document.token = zapsign_create_document_response['token']
            document.open_id = zapsign_create_document_response['open_id']
            document.external_id = zapsign_create_document_response['external_id']
            document.status = zapsign_create_document_response['status']
            document.save()

            document_signers = zapsign_create_document_response.get('signers', [])

            for signer_data, zapsign_signer in zip(signers_data, document_signers):
                Signer.objects.create(
                    document=document,
                    name=signer_data['name'],
                    email=signer_data['email'],
                    token=zapsign_signer.get('token'),
                    external_id=zapsign_signer.get('external_id'),
                    status=zapsign_signer.get('status', 'pending'),
                    sign_url=zapsign_signer.get('sign_url'),
                )

        self._analyze_document_with_ai(document)
        return document
    
    def _analyze_document_with_ai(self, document: Document) -> None:
        try:
            gemini = GeminiClient()

            analysis_result = gemini.analyze_document(
                document_content = document.extracted_text
            )

            document.ai_summary = analysis_result.get('summary', '')
            document.ai_missing_topics = analysis_result.get('missing_topics', [])
            document.ai_insights = analysis_result.get('insights', '')
            document.save()

        except Exception as exception:
            document.ai_summary = 'Analysis unavailable'
            document.ai_missing_topics = []
            document.ai_insights = 'Analysis unavailable'
            document.save()


    def delete_document(self, document: Document) -> None:
        document.deleted_at = timezone.now()
        document.signers.all().update(deleted_at=timezone.now())
        document.save()