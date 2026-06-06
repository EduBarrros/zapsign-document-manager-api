from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DocumentViewSet
from .webhooks import ZapSignWebhookView
from .report_views import ReportView

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = router.urls + [
    path('webhooks/zapsign/', ZapSignWebhookView.as_view(), name='zapsign-webhook'),
    path('reports/', ReportView.as_view(), name='reports'),
]
