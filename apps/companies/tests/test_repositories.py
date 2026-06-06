import pytest
from model_bakery import baker
from django.contrib.auth.models import User

from apps.companies.models import Company
from apps.companies.repositories import CompanyRepository


@pytest.mark.django_db
class TestCompanyRepository:

    def test_get_active_for_user_excludes_deleted(self):
        user = baker.make(User)
        active = baker.make(Company, user=user, deleted_at=None)
        baker.make(Company, user=user, deleted_at='2026-01-01T00:00:00Z')

        result = CompanyRepository().get_active_for_user(user)

        assert list(result) == [active]

    def test_belongs_to_user_returns_true_for_owned_company(self):
        user = baker.make(User)
        company = baker.make(Company, user=user, deleted_at=None)

        assert CompanyRepository().belongs_to_user(company, user) is True

    def test_belongs_to_user_returns_false_for_other_user(self):
        owner = baker.make(User)
        other_user = baker.make(User)
        company = baker.make(Company, user=owner, deleted_at=None)

        assert CompanyRepository().belongs_to_user(company, other_user) is False
