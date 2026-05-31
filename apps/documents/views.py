from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Document
from apps.signers.models import Signer
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(deleted_at__isnull=True)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        document.deleted_at = timezone.now()
        document.save()
        return Response(status=status.HTTP_204_NO_CONTENT)