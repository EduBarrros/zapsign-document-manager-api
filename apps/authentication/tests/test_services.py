import pytest
from django.contrib.auth.models import User

from apps.authentication.services import AuthService
from core.exceptions import AuthenticationException


@pytest.mark.django_db
class TestAuthService:

    def test_signup_creates_user_and_token(self):
        result = AuthService().signup(
            username='novo_admin@teste.com',
            password='senha_segura_123',
        )

        assert result['username'] == 'novo_admin@teste.com'
        assert 'token' in result

    def test_login_with_valid_credentials_returns_token(self):
        User.objects.create_user(
            username='auth_user@teste.com',
            password='corret_password'
        )

        result = AuthService().login(
            username='auth_user@teste.com',
            password='corret_password'
        )

        assert result['username'] == 'auth_user@teste.com'
        assert 'token' in result

    def test_login_with_invalid_password_raises_exception(self):
        User.objects.create_user(
            username='auth_user@teste.com',
            password='corret_password'
        )

        with pytest.raises(AuthenticationException) as exc_info:
            AuthService().login(
                username='auth_user@teste.com',
                password='wrong_password'
            )

        assert exc_info.value.code == "AUTH_INVALID"
        assert str(exc_info.value) == "Credenciais inválidas"