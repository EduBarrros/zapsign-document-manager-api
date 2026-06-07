import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample
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

    @extend_schema(
        tags=["Webhooks"],
        summary="Callback da ZapSign",
        description=(
            "Recebe notificações da ZapSign quando o status de um documento ou signatário é alterado. "
            "Não requer autenticação por token — a validação é feita via header `X-ZapSign-Secret` "
            "quando `ZAPSIGN_WEBHOOK_SECRET` está configurado no ambiente."
        ),
        request=_ZapSignWebhookSerializer,
        examples=[
            OpenApiExample(
                "Documento assinado por todos",
                value={
                    "token": "doc-token-abc123",
                    "status": "signed",
                    "signers": [
                        {"token": "signer-token-xyz", "status": "signed", "sign_url": "https://sandbox.app.zapsign.com.br/verificar/xyz"}
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                "Sucesso",
                value={"data": None, "error": None},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Secret inválido",
                value={"data": None, "error": {"message": "Unauthorized", "code": "WEBHOOK_UNAUTHORIZED"}},
                response_only=True,
                status_codes=["401"],
            ),
        ],
    )
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
