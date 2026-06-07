import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv('DEBUG', 'True') == 'True'

_secret_key = os.getenv('SECRET_KEY')
if not _secret_key:
    if DEBUG:
        _secret_key = 'django-insecure-dev-only-do-not-use-in-production'
    else:
        raise ImproperlyConfigured("A variável de ambiente SECRET_KEY deve ser definida em produção.")
SECRET_KEY = _secret_key

ALLOWED_HOSTS = ['*'] if DEBUG else os.getenv('ALLOWED_HOSTS', '').split(',')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'corsheaders',
]

LOCAL_APPS = [
    'apps.authentication',
    'apps.companies',
    'apps.documents',
    'apps.signers',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'zapsign_db'),
        'USER': os.getenv('DB_USER', 'zapsign_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'zapsign_pass'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'core.exception_handler.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'ZapSign Document Manager API',
    'DESCRIPTION': (
        'API RESTful para gerenciamento de documentos e signatários com integração à plataforma ZapSign '
        'e análise inteligente de conteúdo via Google Gemini AI.\n\n'
        '**Autenticação:** todas as rotas (exceto `/auth/` e `/webhooks/`) exigem o header '
        '`Authorization: Token <seu-token>`.\n\n'
        '**Paginação:** listagens retornam 20 itens por página. Use `?page=2` para navegar.'
    ),
    'VERSION': '1.0.0',
    'TAGS': [
        {
            'name': 'Authentication',
            'description': 'Cadastro e autenticação de usuários. Retorna o token necessário para acessar os demais endpoints.',
        },
        {
            'name': 'Companies',
            'description': 'Gerenciamento de empresas do usuário autenticado. Cada empresa armazena o `api_token` da ZapSign utilizado na criação de documentos.',
        },
        {
            'name': 'Documents',
            'description': (
                'Gerenciamento completo de documentos. Ao criar um documento, o sistema automaticamente:\n'
                '1. Extrai o texto do PDF informado\n'
                '2. Envia o documento para assinatura na ZapSign\n'
                '3. Executa análise de conteúdo com IA (resumo, insights e tópicos ausentes)\n\n'
                'Use `POST /{id}/analyze/` para re-executar a análise de IA a qualquer momento.'
            ),
        },
        {
            'name': 'Signers',
            'description': 'Gerenciamento de signatários vinculados a documentos. Filtros disponíveis: `?status=` e `?document=`.',
        },
        {
            'name': 'Reports',
            'description': 'Relatórios e métricas do usuário autenticado. Retorna totais de documentos e signatários agrupados por status.',
        },
        {
            'name': 'Webhooks',
            'description': (
                'Endpoints chamados por sistemas externos. '
                'O webhook da ZapSign atualiza automaticamente o status de documentos e signatários quando uma assinatura é concluída. '
                'Configure `ZAPSIGN_WEBHOOK_SECRET` no `.env` para validar a autenticidade das requisições.'
            ),
        },
    ],
}

_cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if _cors_origins:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]
elif DEBUG:
    CORS_ALLOWED_ORIGINS = ['http://localhost:4200', 'http://127.0.0.1:4200']
else:
    CORS_ALLOWED_ORIGINS = []

ZAPSIGN_API_URL = os.getenv('ZAPSIGN_API_URL', 'https://sandbox.api.zapsign.com.br/api/v1')
ZAPSIGN_WEBHOOK_SECRET = os.getenv('ZAPSIGN_WEBHOOK_SECRET')
GEMINI_KEY = os.getenv("GEMINI_KEY")
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'apps': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}