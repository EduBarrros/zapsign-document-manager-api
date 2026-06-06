from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserRepository:
    def email_exists(self, email: str) -> bool:
        return User.objects.filter(email=email).exists()

    def create_user(self, *, username: str, password: str) -> User:
        return User.objects.create_user(
            username=username,
            email=username,
            password=password,
        )


class TokenRepository:
    def get_or_create_for_user(self, user: User) -> Token:
        token, _ = Token.objects.get_or_create(user=user)
        return token
