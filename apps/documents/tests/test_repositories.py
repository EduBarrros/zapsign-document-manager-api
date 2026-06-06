import pytest
from model_bakery import baker
from django.contrib.auth.models import User

from apps.companies.models import Company
from apps.documents.models import Document
from apps.documents.repositories import DocumentRepository


@pytest.mark.django_db
class TestDocumentRepository:

    def test_get_active_for_user_filters_by_owner_and_soft_delete(self):
        user = baker.make(User)
        company = baker.make(Company, user=user)
        active = baker.make(Document, company=company, deleted_at=None)
        baker.make(Document, company=company, deleted_at='2026-01-01T00:00:00Z')

        other_company = baker.make(Company, user=baker.make(User))
        baker.make(Document, company=other_company, deleted_at=None)

        result = DocumentRepository().get_active_for_user(user)

        assert list(result) == [active]

    def test_update_zapsign_fields_persists_values(self):
        document = baker.make(Document, token=None, open_id=None)

        DocumentRepository().update_zapsign_fields(
            document,
            token='doc-token',
            open_id=42,
            external_id='ext-1',
            status='pending',
        )

        document.refresh_from_db()
        assert document.token == 'doc-token'
        assert document.open_id == 42
        assert document.external_id == 'ext-1'
        assert document.status == 'pending'
