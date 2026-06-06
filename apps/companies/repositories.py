from django.contrib.auth.models import User
from django.db.models import QuerySet

from apps.common.repositories.base import SoftDeleteRepository

from .models import Company


class CompanyRepository(SoftDeleteRepository[Company]):
    def __init__(self):
        super().__init__(Company)

    def get_active_for_user(self, user: User) -> QuerySet[Company]:
        return self.filter_active(user=user)

    def belongs_to_user(self, company: Company, user: User) -> bool:
        return self.get_active_for_user(user).filter(pk=company.pk).exists()
