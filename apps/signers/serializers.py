from rest_framework import serializers
from .models import Signer

class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        fields = [
            'id',
            'name',
            'email',
            'external_id',
            'status',
            'document',
        ]
        read_only_fields = [
            'status',
            'external_id'
        ]