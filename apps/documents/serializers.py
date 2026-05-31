from rest_framework import serializers
from .models import Document
from apps.signers.serializers import SignerSerializer

class DocumentSerializer(serializers.ModelSerializer):
    signers = SignerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id',
            'name',
            'status',
            'open_id',
            'external_id',
            'created_at',
            'company',
            'signers',
            'ai_missing_topics',
            'ai_insights',
            'ai_summary',
            'created_at',
            'last_updated_at',
        ]
        read_only_fields = [
            'open_id',
            'external_id',
            'created_at',
            'deleted_at',
            'last_updated_at',
            'status',
            'ai_missing_topics',
            'ai_insights',
            'ai_summary'
        ]

class DocumentCreateSerializer(serializers.ModelSerializer):
    signers = SignerSerializer(many=True, read_only=True)

    class Meta: 
        model = Document
        fields = [
            'name',
            'created_at',
            'company',
            'signers',
        ]