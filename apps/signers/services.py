from django.utils import timezone
from .models import Signer


class SignerService:
    @staticmethod
    def soft_delete(company: Signer) -> Signer:
        company.deleted_at = timezone.now()
        company.save(update_fields=["deleted_at"])
        return company