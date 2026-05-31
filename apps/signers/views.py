from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Signer
from .serializers import SignerSerializer

class SignerViewSet(viewsets.ModelViewSet):
    serializer_class = SignerSerializer

    def get_queryset(self):
        return Signer.objects.filter(deleted_at__isnull=True)

    def destroy(self, request, *args, **kwargs):
        signer = self.get_object()
        signer.deleted_at = timezone.now()
        signer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)