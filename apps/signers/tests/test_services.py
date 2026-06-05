import pytest
from model_bakery import baker
from apps.documents.models import Document
from apps.signers.models import Signer
from apps.signers.services import SignerService


@pytest.mark.django_db
class TestSignerService:

    def test_soft_delete_sets_deleted_at_on_signer(self):
        document = baker.make(Document)
        signer = baker.make(Signer, document=document, deleted_at=None)

        updated_signer = SignerService.soft_delete(signer)

        assert updated_signer.deleted_at is not None
        
        signer.refresh_from_db()
        assert signer.deleted_at is not None