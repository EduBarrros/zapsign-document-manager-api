from rest_framework import serializers
from apps.companies.repositories import CompanyRepository
from apps.signers.serializers import SignerNestedSerializer, SignerResponseSerializer
from .models import Document


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
    signers = SignerNestedSerializer(many=True)
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

    def validate_company(self, company):
        request = self.context['request']

        if not CompanyRepository().belongs_to_user(company, request.user):
            raise serializers.ValidationError(
                'Company não pertence ao usuário autenticado'
            )

        return company


class DocumentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['name', 'created_by', 'status']
