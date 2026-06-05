import pytest
from model_bakery import baker
from apps.documents.models import Document
from apps.signers.models import Signer
from apps.signers.serializers import SignerResponseSerializer, SignerRequestSerializer


@pytest.mark.django_db
class TestSignerResponseSerializer:

    def test_serializes_expected_fields(self):
        document = baker.make(Document)
        signer = baker.make(Signer, document=document)
        data = SignerResponseSerializer(signer).data
        
        expected_fields = {
            'id', 'name', 'email', 'token', 
            'external_id', 'status', 'sign_url'
        }
        assert set(data.keys()) == expected_fields

    def test_does_not_expose_deleted_at(self):
        document = baker.make(Document)
        signer = baker.make(Signer, document=document)
        data = SignerResponseSerializer(signer).data
        assert 'deleted_at' not in data


@pytest.mark.django_db
class TestSignerRequestSerializer:

    def test_deserializes_valid_data(self):
        input_data = {
            'name': 'Lucas Silva',
            'email': 'lucas@zapsign.com'
        }
        serializer = SignerRequestSerializer(data=input_data)
        assert serializer.is_valid(), serializer.errors

    def test_rejects_invalid_email(self):
        input_data = {
            'name': 'Lucas Silva',
            'email': 'not-an-email'
        }
        serializer = SignerRequestSerializer(data=input_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_rejects_missing_required_fields(self):
        input_data = {'name': 'Lucas Silva'}  # Faltando email
        serializer = SignerRequestSerializer(data=input_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors