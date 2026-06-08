import json
from django.contrib.auth.models import User
from django.db.models import Count, QuerySet
from django.utils import timezone

from .models import Document


class DocumentRepository:

    def get_active_for_user(self, user: User) -> QuerySet[Document]:
        return Document.objects.filter(
            company__user=user,
            deleted_at__isnull=True,
        )

    def create(self, **data) -> Document:
        return Document.objects.create(**data)

    def update_extracted_text(self, document: Document, text: str) -> Document:
        document.extracted_text = text
        document.save(update_fields=["extracted_text"])
        return document

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
        document.save(update_fields=["token", "open_id", "external_id", "status"])
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
        document.save(update_fields=["ai_summary", "ai_missing_topics", "ai_insights"])
        return document

    def get_summary_for_user(self, user: User) -> dict:
        qs = self.get_active_for_user(user)
        by_status = {
            item['status']: item['count']
            for item in qs.values('status').annotate(count=Count('id'))
        }
        return {'total': qs.count(), 'by_status': by_status}

    def get_by_token(self, token: str) -> Document | None:
        return Document.objects.filter(token=token, deleted_at__isnull=True).first()

    def update_status(self, document: Document, status: str) -> Document:
        document.status = status
        document.save(update_fields=["status"])
        return document

    def update(self, document: Document, **data) -> Document:
        for field, value in data.items():
            setattr(document, field, value)
        document.save(update_fields=list(data.keys()))
        return document

    def soft_delete(self, document: Document) -> Document:
        document.deleted_at = timezone.now()
        document.save(update_fields=["deleted_at"])
        return document