import logging
from django.contrib.auth import authenticate

from .repositories import TokenRepository, UserRepository
from core.exceptions import AuthenticationException

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repository=None, token_repository=None):
        self.user_repository = user_repository or UserRepository()
        self.token_repository = token_repository or TokenRepository()

    def signup(self, *, username: str, password: str) -> dict:
        user = self.user_repository.create_user(
            username=username,
            password=password,
        )

        token = self.token_repository.get_or_create_for_user(user)

        return {
            "token": token.key,
            "username": user.username,
        }

    def login(self, *, username: str, password: str) -> dict:
        user = authenticate(username=username, password=password)

        if not user:
            raise AuthenticationException()

        token = self.token_repository.get_or_create_for_user(user)

        return {
            "token": token.key,
            "username": user.username,
        }