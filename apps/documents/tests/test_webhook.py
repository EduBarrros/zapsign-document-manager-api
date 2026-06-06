import pytest
from unittest.mock import patch
from model_bakery import baker
from rest_framework.test import APIClient
from apps.companies.models import Company
from apps.documents.models import Document
from apps.signers.models import Signer
from django.contrib.auth.models import User


WEBHOOK_URL = '/api/v1/webhooks/zapsign/'


def _payload(document_token='doc-token-123', status='signed', signers=None):
    return {
        'token': document_token,
        'status': status,
        'signers': signers or [],
    }


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def document_with_signer():
    user = baker.make(User)
    company = baker.make(Company, user=user)
    document = baker.make(Document, company=company, token='doc-token-123', status='pending', deleted_at=None)
    signer = baker.make(Signer, document=document, token='signer-token-abc', status='pending')
    return document, signer


@pytest.mark.django_db
class TestZapSignWebhookView:

    def test_updates_document_and_signer_status(self, client, document_with_signer):
        document, signer = document_with_signer
        payload = _payload(signers=[{'token': 'signer-token-abc', 'status': 'signed'}])

        response = client.post(WEBHOOK_URL, payload, format='json')

        assert response.status_code == 200
        document.refresh_from_db()
        signer.refresh_from_db()
        assert document.status == 'signed'
        assert signer.status == 'signed'

    def test_updates_signer_sign_url(self, client, document_with_signer):
        document, signer = document_with_signer
        payload = _payload(signers=[{
            'token': 'signer-token-abc',
            'status': 'signed',
            'sign_url': 'https://app.zapsign.com.br/verificar/abc',
        }])

        client.post(WEBHOOK_URL, payload, format='json')

        signer.refresh_from_db()
        assert signer.sign_url == 'https://app.zapsign.com.br/verificar/abc'

    def test_returns_404_when_document_not_found(self, client):
        payload = _payload(document_token='token-inexistente')

        response = client.post(WEBHOOK_URL, payload, format='json')

        assert response.status_code == 404

    def test_returns_400_for_invalid_payload(self, client):
        response = client.post(WEBHOOK_URL, {}, format='json')

        assert response.status_code == 400

    def test_returns_401_when_secret_is_wrong(self, client, document_with_signer, settings):
        settings.ZAPSIGN_WEBHOOK_SECRET = 'secret-correto'
        payload = _payload()

        response = client.post(
            WEBHOOK_URL,
            payload,
            format='json',
            HTTP_X_ZAPSIGN_SECRET='secret-errado',
        )

        assert response.status_code == 401

    def test_accepts_request_when_secret_is_correct(self, client, document_with_signer, settings):
        settings.ZAPSIGN_WEBHOOK_SECRET = 'secret-correto'
        payload = _payload()

        response = client.post(
            WEBHOOK_URL,
            payload,
            format='json',
            HTTP_X_ZAPSIGN_SECRET='secret-correto',
        )

        assert response.status_code == 200

    def test_accepts_request_when_no_secret_configured(self, client, document_with_signer, settings):
        settings.ZAPSIGN_WEBHOOK_SECRET = None
        payload = _payload()

        response = client.post(WEBHOOK_URL, payload, format='json')

        assert response.status_code == 200

    def test_ignores_unknown_signer_token(self, client, document_with_signer):
        document, _ = document_with_signer
        payload = _payload(signers=[{'token': 'token-inexistente', 'status': 'signed'}])

        response = client.post(WEBHOOK_URL, payload, format='json')

        assert response.status_code == 200
        document.refresh_from_db()
        assert document.status == 'signed'
