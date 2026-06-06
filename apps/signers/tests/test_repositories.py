import pytest
from model_bakery import baker
from django.contrib.auth.models import User

from apps.companies.models import Company
from apps.documents.models import Document
from apps.signers.models import Signer
from apps.signers.repositories import SignerRepository


@pytest.mark.django_db
class TestSignerRepository:

    def test_get_active_for_user_filters_by_document_owner(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        document = baker.make(Document, company=company)
        active = baker.make(Signer, document=document, deleted_at=None)
        baker.make(Signer, document=document, deleted_at='2026-01-01T00:00:00Z')

        other_document = baker.make(Document, company=baker.make(Company, user=baker.make(User)))
        baker.make(Signer, document=other_document, deleted_at=None)

        result = SignerRepository().get_active_for_user(user)

        assert list(result) == [active]

    def test_soft_delete_by_document_marks_all_signers(self):
        document = baker.make(Document)
        signer_one = baker.make(Signer, document=document, deleted_at=None)
        signer_two = baker.make(Signer, document=document, deleted_at=None)

        SignerRepository().soft_delete_by_document(document)

        signer_one.refresh_from_db()
        signer_two.refresh_from_db()
        assert signer_one.deleted_at is not None
        assert signer_two.deleted_at is not None
