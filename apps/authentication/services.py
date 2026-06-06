import logging

from django.contrib.auth import authenticate

from .repositories import TokenRepository, UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository | None = None,
        token_repository: TokenRepository | None = None,
    ):
        self.user_repository = user_repository or UserRepository()
        self.token_repository = token_repository or TokenRepository()

    def signup(self, *, username: str, password: str) -> dict:
        user = self.user_repository.create_user(
            username=username,
            password=password,
        )

        token = self.token_repository.get_or_create_for_user(user)

        logger.info('Usuário cadastrado user_id=%s username=%s', user.id, user.username)

        return {
            'token': token.key,
            'username': user.username,
        }

    def login(self, *, username: str, password: str) -> dict:
        user = authenticate(username=username, password=password)

        if not user:
            logger.warning('Tentativa de login inválida username=%s', username)
            raise ValueError('Credenciais inválidas')

        token = self.token_repository.get_or_create_for_user(user)

        logger.info('Login realizado user_id=%s username=%s', user.id, user.username)

        return {
            'token': token.key,
            'username': user.username
        }
