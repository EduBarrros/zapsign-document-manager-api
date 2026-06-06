from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils import timezone

from apps.documents.models import Document
from .models import Signer


class SignerRepository:

    def get_active_for_user(self, user: User) -> QuerySet[Signer]:
        return Signer.objects.filter(
            document__company__user=user,
            deleted_at__isnull=True,
        )

    def get_active_for_document(self, document: Document) -> QuerySet[Signer]:
        return Signer.objects.filter(
            document=document,
            deleted_at__isnull=True,
        )

    def create_for_document(
        self,
        document: Document,
        *,
        name: str,
        email: str,
        token: str | None = None,
        external_id: str | None = None,
        status: str = "pending",
        sign_url: str | None = None,
    ) -> Signer:
        return Signer.objects.create(
            document=document,
            name=name,
            email=email,
            token=token,
            external_id=external_id,
            status=status,
            sign_url=sign_url,
        )

    def soft_delete(self, signer: Signer) -> Signer:
        signer.deleted_at = timezone.now()
        signer.save(update_fields=["deleted_at"])
        return signer

    def soft_delete_by_document(self, document: Document) -> None:
        Signer.objects.filter(document=document).update(
            deleted_at=timezone.now(),
        )