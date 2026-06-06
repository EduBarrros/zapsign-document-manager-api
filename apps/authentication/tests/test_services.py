import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from apps.companies.models import Company
from apps.authentication.services import AuthService


@pytest.mark.django_db
class TestAuthService:

    def test_signup_creates_user_and_token(self):
        result = AuthService().signup(
            username='novo_admin@teste.com',
            password='senha_segura_123',
        )
        
        assert result['username'] == 'novo_admin@teste.com'
        assert 'token' in result

        user = User.objects.get(username='novo_admin@teste.com')
        assert user.check_password('senha_segura_123')

        assert Token.objects.filter(user=user).exists()

    def test_login_with_valid_credentials_returns_token(self):
        user = User.objects.create_user(
            username='auth_user@teste.com',
            password='corret_password'
        )

        result = AuthService().login(
            username='auth_user@teste.com',
            password='corret_password'
        )

        assert result['username'] == 'auth_user@teste.com'
        assert 'token' in result

    def test_login_with_invalid_password_raises_value_error(self):
        User.objects.create_user(
            username='auth_user@teste.com',
            password='corret_password'
        )

        with pytest.raises(ValueError) as exc_info:
            AuthService().login(
                username='auth_user@teste.com',
                password='wrong_password'
            )

        assert str(exc_info.value) == 'Credenciais inválidas'