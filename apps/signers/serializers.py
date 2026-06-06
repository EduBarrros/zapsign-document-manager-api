from rest_framework import serializers
from .models import Signer


class SignerRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()


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