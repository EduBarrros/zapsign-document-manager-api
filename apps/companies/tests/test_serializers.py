import pytest
from model_bakery import baker
from django.contrib.auth.models import User
from apps.companies.models import Company
from apps.companies.serializers import CompanySerializer


@pytest.mark.django_db
class TestCompanySerializer:

    def test_serializes_company_without_api_token(self):
        company = baker.make(Company, user=baker.make(User), api_token="secret")
        data = CompanySerializer(company).data
        assert "api_token" not in data

    def test_serializes_expected_fields(self):
        company = baker.make(Company, user=baker.make(User), name="Empresa X")
        data = CompanySerializer(company).data
        assert set(data.keys()) == {'id', 'name', 'created_at', 'last_updated_at'}

    def test_deserializes_valid_data(self):
        serializer = CompanySerializer(data={"name": "Empresa X", "api_token": "token123"})
        assert serializer.is_valid()
        assert serializer.validated_data["name"] == "Empresa X"

    def test_read_only_fields_ignored_on_input(self):
        serializer = CompanySerializer(data={
            "name": "Empresa X",
            "api_token": "token123",
            "created_at": "2020-01-01T00:00:00Z"
        })
        assert serializer.is_valid()
        assert "created_at" not in serializer.validated_data