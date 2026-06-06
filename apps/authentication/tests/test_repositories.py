import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from apps.authentication.repositories import TokenRepository, UserRepository


@pytest.mark.django_db
class TestUserRepository:

    def test_email_exists_returns_true_when_user_exists(self):
        User.objects.create_user(
            username='user@teste.com',
            email='user@teste.com',
            password='password123',
        )

        assert UserRepository().email_exists('user@teste.com') is True

    def test_create_user_persists_credentials(self):
        user = UserRepository().create_user(
            username='novo@teste.com',
            password='password123',
        )

        assert user.username == 'novo@teste.com'
        assert user.check_password('password123')


@pytest.mark.django_db
class TestTokenRepository:

    def test_get_or_create_for_user_returns_existing_token(self):
        user = User.objects.create_user(
            username='user@teste.com',
            password='password123',
        )
        existing = Token.objects.create(user=user)

        token = TokenRepository().get_or_create_for_user(user)

        assert token.pk == existing.pk
