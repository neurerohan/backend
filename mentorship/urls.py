from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    MentorProfileViewSet, MentorshipRequestViewSet,
    MentorshipViewSet, MentorReviewViewSet, MentorshipMessageViewSet
)

router = DefaultRouter()
router.register(r'profiles', MentorProfileViewSet, basename='mentor-profile')
router.register(r'requests', MentorshipRequestViewSet, basename='mentorship-request')
router.register(r'mentorships', MentorshipViewSet, basename='mentorship')
router.register(r'reviews', MentorReviewViewSet, basename='mentor-review')

# Nested router for mentorship messages
mentorships_router = routers.NestedSimpleRouter(router, r'mentorships', lookup='mentorship')
mentorships_router.register(r'messages', MentorshipMessageViewSet, basename='mentorship-message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(mentorships_router.urls)),
]
