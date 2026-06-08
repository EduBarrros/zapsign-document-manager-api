from core.exceptions import NotFoundException, ConflictException
from apps.documents.repositories import DocumentRepository
from .models import Signer
from .repositories import SignerRepository


class SignerService:
    def __init__(self, repository: SignerRepository | None = None, document_repository: DocumentRepository | None = None):
        self.repository = repository or SignerRepository()
        self.document_repository = document_repository or DocumentRepository()

    def create_signer(self, user, document_id: int, name: str, email: str) -> Signer:
        document = self.document_repository.get_active_for_user(user).filter(id=document_id).first()
        if not document:
            raise NotFoundException("Documento não encontrado ou sem permissão")
        if self.repository.exists_for_document(document, email):
            raise ConflictException("Já existe um signatário com este email neste documento")
        return self.repository.create_for_document(document, name=name, email=email)

    def update_signer(self, signer: Signer, **data) -> Signer:
        for field, value in data.items():
            setattr(signer, field, value)
        signer.save(update_fields=list(data.keys()))
        return signer

    def soft_delete(self, signer: Signer) -> Signer:
        return self.repository.soft_delete(signer)
