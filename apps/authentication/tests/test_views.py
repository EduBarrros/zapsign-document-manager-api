import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAuthViews:

    def test_signup_endpoint_returns_201_on_success(self):
        client = APIClient()
        payload = {
            'email': 'api_signup@teste.com',
            'password': 'password123',
            'company_name': 'Empresa API'
        }

        response = client.post('/api/v1/auth/signup/', payload, format='json')

        assert response.status_code == 201
        assert 'token' in response.data
        assert response.data['username'] == 'api_signup@teste.com'

    def test_login_endpoint_returns_200_on_success(self):
        client = APIClient()
        User.objects.create_user(username='api_login@teste.com', password='api_password')

        payload = {
            'email': 'api_login@teste.com',
            'password': 'api_password'
        }

        response = client.post('/api/v1/auth/login/', payload, format='json')

        assert response.status_code == 200
        assert 'token' in response.data
        assert response.data['username'] == 'api_login@teste.com'

    def test_login_endpoint_returns_401_on_invalid_credentials(self):
        client = APIClient()
        User.objects.create_user(username='api_login@teste.com', password='api_password')

        payload = {
            'email': 'api_login@teste.com',
            'password': 'password_errado'
        }

        response = client.post('/api/v1/auth/login/', payload, format='json')

        assert response.status_code == 401
        assert 'error' in response.data
        assert response.data['error'] == 'Credenciais inválidas'