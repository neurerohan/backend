from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserSkillViewSet, UserStepProgressViewSet,
    AchievementViewSet, UserAchievementViewSet
)

router = DefaultRouter()
router.register(r'skills', UserSkillViewSet, basename='user-skill')
router.register(r'step-progress', UserStepProgressViewSet, basename='step-progress')
router.register(r'achievements', AchievementViewSet)
router.register(r'user-achievements', UserAchievementViewSet, basename='user-achievement')

urlpatterns = [
    path('', include(router.urls)),
]
