from django.db import models
from apps.documents.models import Document

class Signer(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SIGNED = 'signed', 'Signed'
        REJECTED = 'rejected', 'Rejected'

    document = models.ForeignKey(Document, on_delete=models.PROTECT, related_name='signers')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    token = models.CharField(max_length=255, blank=True, null=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    sign_url = models.URLField(blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Signer'
        verbose_name_plural = 'Signers'

    def __str__(self):
        return f"{self.name} - {self.email}"