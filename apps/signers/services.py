from .models import Signer
from .repositories import SignerRepository


class SignerService:
    def __init__(self, repository: SignerRepository | None = None):
        self.repository = repository or SignerRepository()

    def soft_delete(self, signer: Signer) -> Signer:
        return self.repository.soft_delete(signer)
