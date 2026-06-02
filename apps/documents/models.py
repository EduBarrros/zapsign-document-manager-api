from django.db import models
from apps.companies.models import Company

class Document(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SIGNED = 'signed', 'Signed'
        CANCELLED = 'cancelled', 'Cancelled'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    token = models.CharField(max_length=255, blank=True, null=True)
    open_id = models.IntegerField(blank=True, null=True)
    url_pdf = models.URLField(blank=True, null=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    ai_summary = models.TextField(blank=True, null=True)
    ai_missing_topics = models.JSONField(blank=True, null=True)
    ai_insights = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return self.name
