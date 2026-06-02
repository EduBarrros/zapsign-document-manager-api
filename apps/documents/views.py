from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer, DocumentCreateSerializer
from .services import DocumentService

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentSerializer

    def create(self, request, *args, **kwargs):
        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company = serializer.validated_data['company']
        service = DocumentService()

        try:
            document = service.create_document_with_signers(
                data = serializer.validated_data, 
                company=company
            )
            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as exception:
            return Response(
                {'error': str(exception)},
                status=status.HTTP_502_BAD_GATEWAY
            )

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        document.deleted_at = timezone.now()
        document.save()
        return Response(status=status.HTTP_204_NO_CONTENT)