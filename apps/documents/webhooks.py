import logging

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.response import api_response
from .services import DocumentService

logger = logging.getLogger(__name__)


class _SignerWebhookSerializer(serializers.Serializer):
    token = serializers.CharField()
    status = serializers.CharField()
    sign_url = serializers.URLField(required=False, allow_blank=True)


class _ZapSignWebhookSerializer(serializers.Serializer):
    token = serializers.CharField()
    status = serializers.CharField()
    signers = _SignerWebhookSerializer(many=True, required=False, default=list)


class ZapSignWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not self._is_authorized(request):
            return api_response(
                error="Unauthorized",
                error_code="WEBHOOK_UNAUTHORIZED",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = _ZapSignWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Webhook ZapSign payload inválido errors=%s", serializer.errors)
            return api_response(
                error="Invalid payload",
                error_code="WEBHOOK_INVALID_PAYLOAD",
                status=status.HTTP_400_BAD_REQUEST,
            )

        document = DocumentService().process_zapsign_webhook(serializer.validated_data)

        if not document:
            return api_response(
                error="Document not found",
                error_code="WEBHOOK_DOCUMENT_NOT_FOUND",
                status=status.HTTP_404_NOT_FOUND,
            )

        return api_response(status=status.HTTP_200_OK)

    def _is_authorized(self, request) -> bool:
        secret = getattr(settings, 'ZAPSIGN_WEBHOOK_SECRET', None)
        if not secret:
            return True
        return request.headers.get("X-ZapSign-Secret") == secret
