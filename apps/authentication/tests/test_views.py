import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestAuthViews:

    def test_signup_returns_201(self):
        client = APIClient()

        payload = {
            "email": "api@teste.com",
            "password": "12345678",
        }

        response = client.post("/api/v1/auth/signup/", payload)

        assert response.status_code == 201
        assert response.data["data"]["token"]
        assert response.data["data"]["username"]

    def test_login_success(self):
        client = APIClient()

        User.objects.create_user(
            username="api@teste.com",
            email="api@teste.com",
            password="12345678",
        )

        response = client.post("/api/v1/auth/login/", {
            "email": "api@teste.com",
            "password": "12345678",
        })

        assert response.status_code == 200
        assert response.data["data"]["token"]
        assert response.data["data"]["username"]

    def test_login_invalid_credentials(self):
        client = APIClient()

        User.objects.create_user(
            username="api@teste.com",
            email="api@teste.com",
            password="12345678",
        )

        response = client.post("/api/v1/auth/login/", {
            "email": "api@teste.com",
            "password": "errado123",
        })

        assert response.status_code == 401
        assert response.data["error"]["message"] == "Credenciais inválidas"
        assert response.data["error"]["code"] == "AUTH_INVALID"