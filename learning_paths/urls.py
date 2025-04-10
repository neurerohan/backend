from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import SkillViewSet, LearningPathViewSet, PathStepViewSet, UserLearningPathViewSet

router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'paths', LearningPathViewSet, basename='learning-path')
router.register(r'enrollments', UserLearningPathViewSet, basename='enrollment')

# Nested router for path steps
paths_router = routers.NestedSimpleRouter(router, r'paths', lookup='learning_path')
paths_router.register(r'steps', PathStepViewSet, basename='path-step')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(paths_router.urls)),
]
