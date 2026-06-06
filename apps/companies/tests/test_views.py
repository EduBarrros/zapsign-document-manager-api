import pytest
from model_bakery import baker
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.companies.models import Company


@pytest.fixture
def auth_client():
    user = baker.make(User)
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, user


@pytest.mark.django_db
class TestCompanyViewSet:

    def test_list_returns_only_active_companies(self, auth_client):
        client, user = auth_client
        active = baker.make(Company, user=user, deleted_at=None)
        deleted = baker.make(Company, user=baker.make(User), deleted_at="2020-01-01T00:00:00Z")
        response = client.get('/api/v1/companies/')
        ids = [c['id'] for c in response.data]
        assert active.id in ids
        assert deleted.id not in ids

    def test_delete_soft_deletes_company(self, auth_client):
        client, user = auth_client
        company = baker.make(Company, user=user, deleted_at=None)
        response = client.delete(f'/api/v1/companies/{company.id}/')
        assert response.status_code == 204
        company.refresh_from_db()
        assert company.deleted_at is not None

    def test_unauthenticated_request_returns_401(self):
        client = APIClient()
        response = client.get('/api/v1/companies/')
        assert response.status_code == 401