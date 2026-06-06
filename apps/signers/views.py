from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Signer
from .serializers import SignerRequestSerializer, SignerResponseSerializer 
from drf_spectacular.utils import extend_schema
from .services import SignerService

@extend_schema(tags=["Signers"])
class SignerViewSet(viewsets.ModelViewSet):
    serializer_class = SignerResponseSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SignerRequestSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return Signer.objects.filter(
            document__company__user=self.request.user,
            deleted_at__isnull=True
        )

    def destroy(self, request, *args, **kwargs):
        signer = self.get_object()
        SignerService.soft_delete(signer)
        return Response(status=status.HTTP_204_NO_CONTENT)