from typing import Generic, TypeVar

from django.db.models import Model, QuerySet
from django.utils import timezone

T = TypeVar('T', bound=Model)


class SoftDeleteRepository(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    def get_queryset(self) -> QuerySet[T]:
        return self.model.objects.all()

    def filter_active(self, **filters) -> QuerySet[T]:
        return self.get_queryset().filter(deleted_at__isnull=True, **filters)

    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)

    def soft_delete(self, instance: T) -> T:
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
        return instance
