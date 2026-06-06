from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Document
from .serializers import (
    DocumentResponseSerializer,
    DocumentCreateSerializer
)
from .services import DocumentService


@extend_schema(tags=["Documents"])
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentResponseSerializer

    def get_queryset(self):
        return Document.objects.filter(
            company__user=self.request.user,
            deleted_at__isnull=True
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentResponseSerializer

    def create(self, request, *args, **kwargs):
        serializer = DocumentCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        company = serializer.validated_data['company']

        service = DocumentService()

        try:
            document = service.create_document_with_signers(
                data=dict(serializer.validated_data),
                company=company,
            )

            return Response(
                DocumentResponseSerializer(document).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as exception:
            return Response(
                {'error': str(exception)},
                status=status.HTTP_502_BAD_GATEWAY
            )

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()

        service = DocumentService()
        service.delete_document(document)

        return Response(status=status.HTTP_204_NO_CONTENT)