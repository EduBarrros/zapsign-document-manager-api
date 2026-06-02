from django.utils import timezone
from apps.integrations.zapsign import ZapSignClient
from .models import Document
from apps.signers.models import Signer

class DocumentService:
    def create_document_with_signers(self, data: dict, company) -> Document:
        signers_data = data.pop('signers', [])
        url_pdf = data.get('url_pdf', None)

        document = Document.objects.create(
            name=data['name'],
            created_by=data['created_by'],
            company=company,
            url_pdf=url_pdf,
        )

        try:
            client = ZapSignClient(api_token=company.api_token)
            
            zapsign_create_document_response = client.create_document(
                name=document.name,
                url_pdf=document.url_pdf,
                signers=signers_data
            )

            document.token = zapsign_create_document_response['token']
            document.open_id = zapsign_create_document_response['open_id']
            document.external_id = zapsign_create_document_response['external_id']
            document.status = zapsign_create_document_response['status']
            document.save()

            document_signers = zapsign_create_document_response.get('signers', [])

            for signer_data, zapsign_signer in zip(signers_data, document_signers):
                Signer.objects.create(
                    document=document,
                    name=signer_data['name'],
                    email=signer_data['email'],
                    token=zapsign_signer.get('token'),
                    external_id=zapsign_signer.get('external_id'),
                    status=zapsign_signer.get('status', 'pending'),
                    sign_url=zapsign_signer.get('sign_url'),
                )
        
        except Exception as exception:
            document.delete()
            raise exception

        return document

    def delete_document(self, document: Document) -> None:
        document.deleted_at = timezone.now()
        document.signers.all().update(deleted_at=timezone.now())
        document.save()