import pytest
from model_bakery import baker
from django.contrib.auth.models import User
from apps.companies.models import Company
from apps.documents.models import Document
from apps.documents.serializers import DocumentResponseSerializer, DocumentCreateSerializer


@pytest.mark.django_db
class TestDocumentResponseSerializer:

    def test_serializes_expected_fields(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        document = baker.make(Document, company=company)
        data = DocumentResponseSerializer(document).data
        expected_fields = {
            'id', 'name', 'status', 'open_id', 'token', 'url_pdf',
            'external_id', 'created_at', 'created_by', 'company',
            'signers', 'ai_summary', 'ai_missing_topics', 'ai_insights',
            'last_updated_at'
        }
        assert set(data.keys()) == expected_fields

    def test_does_not_expose_deleted_at(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        document = baker.make(Document, company=company)
        data = DocumentResponseSerializer(document).data
        assert 'deleted_at' not in data

    def test_includes_nested_signers(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        document = baker.make(Document, company=company)
        from apps.signers.models import Signer
        baker.make(Signer, document=document, _quantity=2)
        data = DocumentResponseSerializer(document).data
        assert len(data['signers']) == 2


@pytest.mark.django_db
class TestDocumentCreateSerializer:

    def test_deserializes_valid_data(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        input_data = {
            'name': 'Contrato de Teste',
            'created_by': 'admin@teste.com',
            'company': company.id,
            'url_pdf': 'https://example.com/doc.pdf',
            'signers': [
                {'name': 'João Silva', 'email': 'joao@teste.com'}
            ]
        }
        serializer = DocumentCreateSerializer(data=input_data)
        assert serializer.is_valid(), serializer.errors

    def test_rejects_invalid_url_pdf(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        input_data = {
            'name': 'Contrato',
            'created_by': 'admin@teste.com',
            'company': company.id,
            'url_pdf': 'not-a-url',
            'signers': [{'name': 'João', 'email': 'joao@teste.com'}]
        }
        serializer = DocumentCreateSerializer(data=input_data)
        assert not serializer.is_valid()
        assert 'url_pdf' in serializer.errors

    def test_rejects_invalid_signer_email(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        input_data = {
            'name': 'Contrato',
            'created_by': 'admin@teste.com',
            'company': company.id,
            'url_pdf': 'https://example.com/doc.pdf',
            'signers': [{'name': 'João', 'email': 'not-an-email'}]
        }
        serializer = DocumentCreateSerializer(data=input_data)
        assert not serializer.is_valid()