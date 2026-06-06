import logging

from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import SignerRequestSerializer, SignerResponseSerializer
from drf_spectacular.utils import extend_schema
from .services import SignerService
from .repositories import SignerRepository

logger = logging.getLogger(__name__)


@extend_schema(tags=["Signers"])
class SignerViewSet(viewsets.ModelViewSet):
    serializer_class = SignerResponseSerializer

    def __init__(self, *args, signer_repository=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.signer_repository = signer_repository or SignerRepository()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SignerRequestSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return self.signer_repository.get_active_for_user(self.request.user)

    def perform_create(self, serializer):
        signer = serializer.save()
        logger.info(
            'Signatário criado signer_id=%s document_id=%s user_id=%s',
            signer.id,
            signer.document_id,
            self.request.user.id,
        )

    def destroy(self, request, *args, **kwargs):
        signer = self.get_object()
        logger.info(
            'Soft delete de signatário signer_id=%s document_id=%s user_id=%s',
            signer.id,
            signer.document_id,
            request.user.id,
        )
        SignerService().soft_delete(signer)
        return Response(status=status.HTTP_204_NO_CONTENT)
