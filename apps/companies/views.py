import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from core.response import api_response

from .serializers import CompanySerializer
from .services import CompanyService

logger = logging.getLogger(__name__)

_COMPANY_EXAMPLE = {
    "id": 1,
    "name": "Acme Ltda",
    "created_at": "2024-01-15T10:00:00Z",
    "last_updated_at": "2024-01-15T10:00:00Z",
}

_COMPANY_REQUEST_EXAMPLE = OpenApiExample(
    "Criar empresa",
    value={"name": "Acme Ltda", "api_token": "seu-token-zapsign"},
    request_only=True,
)

_COMPANY_RESPONSE_EXAMPLE = OpenApiExample(
    "Empresa criada",
    value={"data": _COMPANY_EXAMPLE, "error": None},
    response_only=True,
    status_codes=["200", "201"],
)


@extend_schema(tags=["Companies"])
@extend_schema(
    methods=["GET"],
    summary="Listar empresas",
    description="Retorna todas as empresas ativas do usuário autenticado, paginadas.",
    examples=[
        OpenApiExample(
            "Lista de empresas",
            value={"count": 1, "next": None, "previous": None, "results": [_COMPANY_EXAMPLE]},
            response_only=True,
        )
    ],
)
@extend_schema(
    methods=["POST"],
    summary="Criar empresa",
    description="Cadastra uma nova empresa vinculada ao usuário. O `api_token` é o token gerado na sua conta ZapSign (sandbox ou produção).",
    examples=[_COMPANY_REQUEST_EXAMPLE, _COMPANY_RESPONSE_EXAMPLE],
)
@extend_schema(
    methods=["PUT"],
    summary="Atualizar empresa",
    description="Substitui completamente os dados da empresa. Útil para rotacionar o `api_token` da ZapSign.",
    examples=[
        OpenApiExample(
            "Payload completo",
            value={"name": "Acme Ltda Atualizada", "api_token": "novo-token-zapsign"},
            request_only=True,
        ),
        OpenApiExample(
            "Empresa atualizada",
            value={"data": _COMPANY_EXAMPLE, "error": None},
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
@extend_schema(
    methods=["PATCH"],
    summary="Atualizar empresa parcialmente",
    description="Atualiza apenas os campos informados. Útil para rotacionar somente o `api_token` sem alterar o nome.",
    examples=[
        OpenApiExample(
            "Apenas token",
            value={"api_token": "novo-token-zapsign"},
            request_only=True,
        ),
        OpenApiExample(
            "Empresa atualizada",
            value={"data": _COMPANY_EXAMPLE, "error": None},
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
@extend_schema(
    methods=["DELETE"],
    summary="Remover empresa",
    description="Realiza soft delete da empresa. Documentos vinculados não são removidos, apenas a empresa é excluída das listagens.",
)
class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return CompanyService().get_active_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = CompanyService().create_company(
            user=request.user,
            **serializer.validated_data,
        )

        logger.info(
            "Empresa criada company_id=%s user_id=%s name=%s",
            company.id,
            request.user.id,
            company.name,
        )

        return api_response(
            data=CompanySerializer(company).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        company = self.get_object()
        serializer = self.get_serializer(company, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        company = CompanyService().update_company(company, **serializer.validated_data)

        logger.info("Empresa atualizada company_id=%s user_id=%s", company.id, request.user.id)
        return api_response(data=CompanySerializer(company).data)

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()

        CompanyService().soft_delete(company)

        logger.info(
            "Soft delete de empresa company_id=%s user_id=%s",
            company.id,
            request.user.id,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)