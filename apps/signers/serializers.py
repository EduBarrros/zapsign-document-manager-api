from rest_framework import serializers
from .models import Signer


class SignerNestedSerializer(serializers.Serializer):
    """Usado apenas quando signatários chegam aninhados na criação de documento."""
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()


class SignerRequestSerializer(serializers.Serializer):
    """Usado no POST /signers/ — criação avulsa, exige document existente."""
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    document = serializers.IntegerField(help_text="ID do documento ao qual o signatário será associado")


class SignerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        fields = ['name', 'email']


class SignerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        fields = [
            'id',
            'name',
            'email',
            'token',
            'external_id',
            'status',
            'sign_url',
        ]
        read_only_fields = fields