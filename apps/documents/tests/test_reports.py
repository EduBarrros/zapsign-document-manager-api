import pytest
from model_bakery import baker
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.companies.models import Company
from apps.documents.models import Document
from apps.signers.models import Signer


REPORTS_URL = '/api/v1/reports/'


@pytest.fixture
def auth_client():
    user = baker.make(User)
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, user


@pytest.mark.django_db
class TestReportView:

    def test_returns_document_totals(self, auth_client):
        client, user = auth_client
        company = baker.make(Company, user=user)
        baker.make(Document, company=company, status='pending', deleted_at=None)
        baker.make(Document, company=company, status='pending', deleted_at=None)
        baker.make(Document, company=company, status='signed', deleted_at=None)

        response = client.get(REPORTS_URL)

        assert response.status_code == 200
        docs = response.data['data']['documents']
        assert docs['total'] == 3
        assert docs['by_status']['pending'] == 2
        assert docs['by_status']['signed'] == 1

    def test_returns_signer_totals(self, auth_client):
        client, user = auth_client
        company = baker.make(Company, user=user)
        document = baker.make(Document, company=company, deleted_at=None)
        baker.make(Signer, document=document, status='signed', deleted_at=None)
        baker.make(Signer, document=document, status='pending', deleted_at=None)

        response = client.get(REPORTS_URL)

        assert response.status_code == 200
        signers = response.data['data']['signers']
        assert signers['total'] == 2
        assert signers['by_status']['signed'] == 1
        assert signers['by_status']['pending'] == 1

    def test_excludes_deleted_documents(self, auth_client):
        client, user = auth_client
        company = baker.make(Company, user=user)
        baker.make(Document, company=company, deleted_at=None)
        baker.make(Document, company=company, deleted_at='2020-01-01T00:00:00Z')

        response = client.get(REPORTS_URL)

        assert response.data['data']['documents']['total'] == 1

    def test_excludes_other_user_documents(self, auth_client):
        client, user = auth_client
        company = baker.make(Company, user=user)
        baker.make(Document, company=company, deleted_at=None)

        other_user = baker.make(User)
        other_company = baker.make(Company, user=other_user)
        baker.make(Document, company=other_company, deleted_at=None)

        response = client.get(REPORTS_URL)

        assert response.data['data']['documents']['total'] == 1

    def test_unauthenticated_returns_401(self):
        client = APIClient()
        response = client.get(REPORTS_URL)
        assert response.status_code == 401

    def test_returns_zeros_when_no_data(self, auth_client):
        client, user = auth_client

        response = client.get(REPORTS_URL)

        assert response.status_code == 200
        assert response.data['data']['documents']['total'] == 0
        assert response.data['data']['signers']['total'] == 0
