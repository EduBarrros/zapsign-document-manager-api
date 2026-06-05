import pytest
from model_bakery import baker
from django.contrib.auth.models import User
from apps.authentication.serializers import SignupRequestSerializer, LoginRequestSerializer


@pytest.mark.django_db
class TestSignupRequestSerializer:

    def test_deserializes_valid_signup_data(self):
        input_data = {
            'email': 'novo_usuario@teste.com',
            'password': 'password123',
            'company_name': 'Minha Empresa',
            'zap_sign_api_token': 'token_secreto_123'
        }
        serializer = SignupRequestSerializer(data=input_data)
        assert serializer.is_valid(), serializer.errors

    def test_rejects_existing_email(self):
        baker.make(User, email='ja_existe@teste.com')
        
        input_data = {
            'email': 'ja_existe@teste.com',
            'password': 'password123',
            'company_name': 'Empresa Teste',
            'zap_sign_api_token': 'token123'
        }
        serializer = SignupRequestSerializer(data=input_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_rejects_short_password(self):
        input_data = {
            'email': 'usuario@teste.com',
            'password': 'short',
            'company_name': 'Empresa Teste',
            'zap_sign_api_token': 'token123'
        }
        serializer = SignupRequestSerializer(data=input_data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_rejects_empty_zap_sign_api_token(self):
        input_data = {
            'email': 'usuario@teste.com',
            'password': 'password123',
            'company_name': 'Empresa Teste',
            'zap_sign_api_token': '   '
        }
        serializer = SignupRequestSerializer(data=input_data)
        assert not serializer.is_valid()
        assert 'zap_sign_api_token' in serializer.errors


class TestLoginRequestSerializer:

    def test_deserializes_valid_login_data(self):
        input_data = {
            'email': 'login@teste.com',
            'password': 'password123'
        }
        serializer = LoginRequestSerializer(data=input_data)
        assert serializer.is_valid(), serializer.errors