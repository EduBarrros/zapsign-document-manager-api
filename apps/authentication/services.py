from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from apps.companies.models import Company

class AuthService:

    @staticmethod
    def signup(*, username: str, password: str, company_name: str, api_token: str) -> dict:
        user = User.objects.create_user(
            username = username,
            password = password
        )

        token, _ = Token.objects.get_or_create(user=user)

        Company.objects.create(
            user=user,
            name=company_name,
            api_token=api_token
        )

        return {
            'token': token.key,
            'username': user.username,
            'company_name': company_name
        }
    
    @staticmethod
    def login(*, username: str, password: str) -> dict:
        user = authenticate(username=username, password=password)

        if not user:
            raise ValueError('Credenciais inválidas')
        
        token, _ = Token.objects.get_or_create(user=user)

        return {
            'token': token.key,
            'username': user.username
        }