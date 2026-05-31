from rest_framework.routers import DefaultRouter
from .views import SignerViewSet

router = DefaultRouter()

router.register(r'signers', SignerViewSet, basename='signer')

urlpatterns = router.urls