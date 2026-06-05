from rest_framework import serializers
from .models import Document
from apps.signers.serializers import SignerRequestSerializer, SignerResponseSerializer


class DocumentResponseSerializer(serializers.ModelSerializer):
    signers = SignerResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id',
            'name',
            'status',
            'open_id',
            'token',
            'url_pdf',
            'external_id',
            'created_at',
            'created_by',
            'company',
            'signers',
            'ai_summary',
            'ai_missing_topics',
            'ai_insights',
            'last_updated_at',
        ]
        read_only_fields = fields


class DocumentCreateSerializer(serializers.ModelSerializer):
    signers = SignerRequestSerializer(many=True)
    url_pdf = serializers.URLField()

    class Meta:
        model = Document
        fields = [
            'name',
            'created_by',
            'company',
            'url_pdf',
            'signers',
        ]