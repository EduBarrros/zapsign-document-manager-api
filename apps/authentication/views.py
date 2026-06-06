from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from core.response import api_response
from core.exceptions import AuthenticationException
from .services import AuthService
from .serializers import SignupRequestSerializer, LoginRequestSerializer

class SignupView(APIView):
    permission_classes = [AllowAny]

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