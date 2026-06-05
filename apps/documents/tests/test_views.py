import pytest
from unittest.mock import patch
from model_bakery import baker
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.companies.models import Company
from apps.documents.models import Document


@pytest.fixture
def auth_client():
    user = baker.make(User)
    company = baker.make(Company, user=user)
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, user, company


@pytest.mark.django_db
class TestDocumentViewSet:

    def test_list_returns_only_active_documents(self, auth_client):
        client, user, company = auth_client
        active = baker.make(Document, company=company, deleted_at=None)
        deleted = baker.make(Document, company=company, deleted_at='2020-01-01T00:00:00Z')
        response = client.get('/api/v1/documents/')
        ids = [d['id'] for d in response.data]
        assert active.id in ids
        assert deleted.id not in ids

    def test_list_does_not_return_other_company_documents(self, auth_client):
        client, user, company = auth_client
        other_user = baker.make(User)
        other_company = baker.make(Company, user=other_user)
        own_document = baker.make(Document, company=company, deleted_at=None)
        other_document = baker.make(Document, company=other_company, deleted_at=None)
        response = client.get('/api/v1/documents/')
        ids = [d['id'] for d in response.data]
        assert own_document.id in ids
        assert other_document.id not in ids

    def test_delete_soft_deletes_document(self, auth_client):
        client, user, company = auth_client
        document = baker.make(Document, company=company, deleted_at=None)
        response = client.delete(f'/api/v1/documents/{document.id}/')
        assert response.status_code == 204
        document.refresh_from_db()
        assert document.deleted_at is not None

    def test_unauthenticated_request_returns_401(self):
        client = APIClient()
        response = client.get('/api/v1/documents/')
        assert response.status_code == 401

    @patch('apps.documents.views.DocumentService')
    def test_create_returns_502_if_zapsign_fails(self, mock_service, auth_client):
        client, user, company = auth_client
        mock_service.return_value.create_document_with_signers.side_effect = Exception('ZapSign error')
        
        payload = {
            'name': 'Contrato',
            'created_by': user.id,     
            'company': company.id,     
            'url_pdf': 'https://example.com/doc.pdf',
            'signers': [{'name': 'João', 'email': 'joao@teste.com'}]
        }
        
        response = client.post('/api/v1/documents/', payload, format='json')
        
        assert response.status_code == 502