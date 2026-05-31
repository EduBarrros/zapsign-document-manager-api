from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    api_token = serializers.CharField(write_only=True)

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'api_token',
            'created_at',
            'last_updated_at',
        ]
        read_only_fields = [
            'created_at',
            'last_updated_at',
        ]