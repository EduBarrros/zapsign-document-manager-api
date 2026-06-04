from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company'
    )
    name = models.CharField(max_length=255)
    api_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name