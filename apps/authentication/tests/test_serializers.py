import pytest
from model_bakery import baker
from django.contrib.auth.models import User
from apps.authentication.serializers import SignupRequestSerializer


@pytest.mark.django_db
class TestSignupRequestSerializer:

    def test_accepts_valid_data(self):
        input_data = {
            "email": "novo@teste.com",
            "password": "password123",
            "company_name": "Empresa Teste",
        }
        serializer = SignupRequestSerializer(data=input_data)
        assert serializer.is_valid()

    def test_rejects_existing_email(self):
        baker.make(User, username="ja_existe@teste.com", email="ja_existe@teste.com")

        input_data = {
            "email": "ja_existe@teste.com",
            "password": "password123",
            "company_name": "Empresa Teste",
        }
        serializer = SignupRequestSerializer(data=input_data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_rejects_short_password(self):
        input_data = {
            "email": "novo@teste.com",
            "password": "123",
        }
        serializer = SignupRequestSerializer(data=input_data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors