from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils import timezone

from apps.common.repositories.base import SoftDeleteRepository
from apps.documents.models import Document

from .models import Signer


class SignerRepository(SoftDeleteRepository[Signer]):
    def __init__(self):
        super().__init__(Signer)

    def get_active_for_user(self, user: User) -> QuerySet[Signer]:
        return self.filter_active(document__company__user=user)

    def create_for_document(
        self,
        document: Document,
        *,
        name: str,
        email: str,
        token: str | None = None,
        external_id: str | None = None,
        status: str = 'pending',
        sign_url: str | None = None,
    ) -> Signer:
        return self.create(
            document=document,
            name=name,
            email=email,
            token=token,
            external_id=external_id,
            status=status,
            sign_url=sign_url,
        )

    def soft_delete_by_document(self, document: Document) -> None:
        document.signers.all().update(deleted_at=timezone.now())
