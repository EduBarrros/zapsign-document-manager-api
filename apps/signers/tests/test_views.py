import pytest
from unittest.mock import patch
from model_bakery import baker
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.companies.models import Company
from apps.documents.models import Document
from apps.signers.models import Signer


@pytest.fixture
def auth_client():
    user = baker.make(User)
    company = baker.make(Company, user=user)
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, user, company


@pytest.mark.django_db
class TestSignerViewSet:

    def test_list_returns_only_active_signers(self, auth_client):
        client, user, company = auth_client
        document = baker.make(Document, company=company)
        
        active_signer = baker.make(Signer, document=document, deleted_at=None)
        deleted_signer = baker.make(Signer, document=document, deleted_at='2026-01-01T00:00:00Z')
        
        response = client.get('/api/v1/signers/')
        assert response.status_code == 200
        
        ids = [signer['id'] for signer in response.data]
        assert active_signer.id in ids
        assert deleted_signer.id not in ids

    @patch('apps.signers.views.SignerService')
    def test_delete_calls_service_soft_delete(self, mock_service, auth_client):
        client, user, company = auth_client
        document = baker.make(Document, company=company)
        signer = baker.make(Signer, document=document, deleted_at=None)

        response = client.delete(f'/api/v1/signers/{signer.id}/')
        
        assert response.status_code == 204
        mock_service.soft_delete.assert_called_once_with(signer)

    def test_unauthenticated_request_returns_401(self):
        client = APIClient()
        response = client.get('/api/v1/signers/')
        assert response.status_code == 401