from rest_framework import serializers
from .models import Signer

class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        fields = [
            'id',
            'name',
            'email',
            'token',
            'sign_url',
            'external_id',
            'status',
        ]
        read_only_fields = [
            'status',
            'external_id',
            'token',
            'sign_url'
        ]
        extra_kwargs = {
            'document': {'required': False}
        }