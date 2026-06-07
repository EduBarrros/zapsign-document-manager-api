from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.renderers import JSONRenderer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.authentication.urls')),
    path('api/v1/', include('apps.companies.urls')),
    path('api/v1/', include('apps.documents.urls')),
    path('api/v1/', include('apps.signers.urls')),
    path('api/schema/', SpectacularAPIView.as_view(renderer_classes=[JSONRenderer]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')
]
