from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample
from core.response import api_response
from core.exceptions import AuthenticationException
from .services import AuthService
from .serializers import SignupRequestSerializer, LoginRequestSerializer, SignupResponseSerializer, LoginResponseSerializer


class SignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Cadastrar novo usuário",
        description="Cria um novo usuário e retorna o token de autenticação para uso imediato.",
        request=SignupRequestSerializer,
        responses={201: SignupResponseSerializer},
        examples=[
            OpenApiExample(
                "Exemplo de cadastro",
                value={"email": "usuario@empresa.com", "password": "senha1234"},
                request_only=True,
            ),
            OpenApiExample(
                "Resposta de sucesso",
                value={"data": {"token": "abc123token", "username": "usuario@empresa.com"}, "error": None},
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request):
        serializer = SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AuthService().signup(
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        return api_response(
            data=result,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Autenticar usuário",
        description="Autentica o usuário com e-mail e senha. Retorna o token que deve ser enviado no header `Authorization: Token <token>` em todas as requisições autenticadas.",
        request=LoginRequestSerializer,
        responses={200: LoginResponseSerializer},
        examples=[
            OpenApiExample(
                "Exemplo de login",
                value={"email": "usuario@empresa.com", "password": "senha1234"},
                request_only=True,
            ),
            OpenApiExample(
                "Resposta de sucesso",
                value={"data": {"token": "abc123token", "username": "usuario@empresa.com"}, "error": None},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Credenciais inválidas",
                value={"data": None, "error": {"message": "Credenciais inválidas", "code": "AUTH_ERROR"}},
                response_only=True,
                status_codes=["401"],
            ),
        ],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AuthService().login(
                username=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

            return api_response(data=result)

        except AuthenticationException as exc:
            return api_response(
                error=str(exc),
                error_code=getattr(exc, "code", "AUTH_ERROR"),
                status=status.HTTP_401_UNAUTHORIZED,
            )