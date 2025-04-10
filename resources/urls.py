from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ResourceTypeViewSet, ResourceProviderViewSet, ResourceViewSet,
    UserResourceViewSet, ResourceRecommendationViewSet
)

router = DefaultRouter()
router.register(r'types', ResourceTypeViewSet)
router.register(r'providers', ResourceProviderViewSet)
router.register(r'all', ResourceViewSet)
router.register(r'user', UserResourceViewSet, basename='user-resource')
router.register(r'recommendations', ResourceRecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
]
