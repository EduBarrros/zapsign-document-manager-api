from django.contrib.auth.models import User
from django.db.models import QuerySet

from apps.common.repositories.base import SoftDeleteRepository

from .models import Document


class DocumentRepository(SoftDeleteRepository[Document]):
    def __init__(self):
        super().__init__(Document)

    def get_active_for_user(self, user: User) -> QuerySet[Document]:
        return self.filter_active(company__user=user)

    def update_zapsign_fields(
        self,
        document: Document,
        *,
        token: str,
        open_id: int,
        external_id: str,
        status: str,
    ) -> Document:
        document.token = token
        document.open_id = open_id
        document.external_id = external_id
        document.status = status
        document.save()
        return document

    def update_ai_analysis(
        self,
        document: Document,
        *,
        summary: str,
        missing_topics: list,
        insights: str,
    ) -> Document:
        document.ai_summary = summary
        document.ai_missing_topics = missing_topics
        document.ai_insights = insights
        document.save()
        return document
