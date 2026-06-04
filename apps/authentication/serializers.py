from django.contrib.auth.models import User
from rest_framework import serializers

class SignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    company_name = serializers.CharField(max_length=255)
    zap_sign_api_token = serializers.CharField(max_length=255)

    def validate_email(self, value):
        if(User.objects.filter(email=value).exists()):
            raise serializers.ValidationError("Email já cadastrado")
        return value
    
    def validate_zap_sign_api_token(self, value):
        if not value.strip():
            raise serializers.ValidationError("Token da API não pode estar vazio")
        return value
    
class SignupResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()
    company_name = serializers.CharField()

class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()