import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .services import AuthService
from .serializers import (
    SignupRequestSerializer,
    SignupResponseSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer
)

logger = logging.getLogger(__name__)


class SignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        request=SignupRequestSerializer,
        responses={201: SignupResponseSerializer},
        summary='Cadastro de usuário',
        description='Cria um novo usuário e retorna o token de autenticação.'
    )
    def post(self, request):
        request_serializer = SignupRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        email = request_serializer.validated_data['email']

        try:
            result = AuthService().signup(
                username=email,
                password=request_serializer.validated_data['password'],
            )
        except Exception:
            logger.error('Erro ao cadastrar usuário username=%s', email, exc_info=True)
            raise

        response_serializer = SignupResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        request=LoginRequestSerializer,
        responses={200: LoginResponseSerializer},
        summary='Login',
        description='Autentica com email e senha. Retorna o token de autenticação.',
    )
    def post(self, request):
        request_serializer = LoginRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        email = request_serializer.validated_data['email']

        try:
            result = AuthService().login(
                username=email,
                password=request_serializer.validated_data['password']
            )
        except ValueError as e:
            logger.warning('Login rejeitado username=%s', email)
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response_serializer = LoginResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
