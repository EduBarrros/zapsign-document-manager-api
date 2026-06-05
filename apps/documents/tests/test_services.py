import pytest
from unittest.mock import patch, MagicMock
from model_bakery import baker
from django.contrib.auth.models import User
from apps.companies.models import Company
from apps.documents.models import Document
from apps.documents.services import DocumentService
from apps.signers.models import Signer


@pytest.mark.django_db
class TestDocumentService:

    def _make_zapsign_response(self):
        return {
            'token': 'doc-token-123',
            'open_id': 1,
            'external_id': 'ext-123',
            'status': 'pending',
            'signers': [
                {
                    'token': 'signer-token-123',
                    'external_id': 'signer-ext-123',
                    'status': 'new',
                    'sign_url': 'https://sandbox.app.zapsign.com.br/verificar/123',
                }
            ]
        }

    @patch('apps.documents.services.ZapSignClient')
    @patch('apps.documents.services.GeminiClient')
    @patch('apps.documents.services.PDFExtractor')
    def test_creates_document_with_signers(self, mock_pdf, mock_gemini, mock_zapsign):
        mock_zapsign.return_value.create_document.return_value = self._make_zapsign_response()
        mock_gemini.return_value.analyze_document.return_value = {
            'summary': 'Resumo',
            'missing_topics': [],
            'insights': 'Insights'
        }
        mock_pdf.extract_from_url.return_value = 'texto extraido'

        user = baker.make(User)
        company = baker.make(Company, user=user, api_token='token-zapsign')

        service = DocumentService()
        data = {
            'name': 'Contrato Teste',
            'created_by': 'admin@teste.com',
            'url_pdf': 'https://example.com/doc.pdf',
            'signers': [{'name': 'João', 'email': 'joao@teste.com'}]
        }

        document = service.create_document_with_signers(data=data, company=company)

        assert document.token == 'doc-token-123'
        assert document.open_id == 1
        assert document.status == 'pending'
        assert Signer.objects.filter(document=document).count() == 1

    @patch('apps.documents.services.ZapSignClient')
    @patch('apps.documents.services.PDFExtractor')
    def test_rolls_back_if_zapsign_fails(self, mock_pdf, mock_zapsign):
        mock_zapsign.return_value.create_document.side_effect = Exception('ZapSign error')
        mock_pdf.extract_from_url.return_value = 'texto'

        user = baker.make(User)
        company = baker.make(Company, user=user, api_token='token-zapsign')

        service = DocumentService()
        data = {
            'name': 'Contrato Falho',
            'created_by': 'admin@teste.com',
            'url_pdf': 'https://example.com/doc.pdf',
            'signers': [{'name': 'João', 'email': 'joao@teste.com'}]
        }

        with pytest.raises(Exception):
            service.create_document_with_signers(data=data, company=company)

        assert Document.objects.filter(name='Contrato Falho').count() == 0

    @patch('apps.documents.services.ZapSignClient')
    @patch('apps.documents.services.GeminiClient')
    @patch('apps.documents.services.PDFExtractor')
    def test_ai_failure_does_not_rollback_document(self, mock_pdf, mock_gemini, mock_zapsign):
        mock_zapsign.return_value.create_document.return_value = self._make_zapsign_response()
        mock_gemini.return_value.analyze_document.side_effect = Exception('Gemini error')
        mock_pdf.extract_from_url.return_value = 'texto'

        user = baker.make(User)
        company = baker.make(Company, user=user, api_token='token-zapsign')

        service = DocumentService()
        data = {
            'name': 'Contrato IA Falha',
            'created_by': 'admin@teste.com',
            'url_pdf': 'https://example.com/doc.pdf',
            'signers': [{'name': 'João', 'email': 'joao@teste.com'}]
        }

        document = service.create_document_with_signers(data=data, company=company)

        assert document is not None
        assert document.ai_summary == 'Analysis unavailable'

    @pytest.mark.django_db
    def test_soft_delete_sets_deleted_at_on_document_and_signers(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        document = baker.make(Document, company=company, deleted_at=None)
        signer = baker.make('signers.Signer', document=document, deleted_at=None)

        service = DocumentService()
        service.delete_document(document)

        document.refresh_from_db()
        signer.refresh_from_db()

        assert document.deleted_at is not None
        assert signer.deleted_at is not None