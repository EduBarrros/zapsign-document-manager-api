import pytest
from model_bakery import baker
from django.contrib.auth.models import User
from django.utils import timezone
from apps.companies.models import Company
from apps.companies.services import CompanyService


@pytest.mark.django_db
class TestCompanyService:

    def test_soft_delete_sets_deleted_at(self):
        company = baker.make(Company, user=baker.make(User), deleted_at=None)
        CompanyService.soft_delete(company)
        company.refresh_from_db()
        assert company.deleted_at is not None

    def test_soft_delete_does_not_remove_from_database(self):
        company = baker.make(Company, user=baker.make(User))
        CompanyService.soft_delete(company)
        assert Company.objects.filter(id=company.id).exists()

    def test_soft_deleted_company_not_in_active_queryset(self):
        company = baker.make(Company, user=baker.make(User))
        CompanyService.soft_delete(company)
        active = Company.objects.filter(deleted_at__isnull=True)
        assert company not in active