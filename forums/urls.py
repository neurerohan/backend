from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    ForumCategoryViewSet, ForumTopicViewSet, ForumPostViewSet,
    StudyGroupViewSet, StudyGroupMemberViewSet, StudyGroupMessageViewSet
)

router = DefaultRouter()
router.register(r'categories', ForumCategoryViewSet)
router.register(r'topics', ForumTopicViewSet, basename='forum-topic')
router.register(r'groups', StudyGroupViewSet, basename='study-group')

# Nested router for forum posts
topics_router = routers.NestedSimpleRouter(router, r'topics', lookup='topic')
topics_router.register(r'posts', ForumPostViewSet, basename='forum-post')

# Nested router for study group members and messages
groups_router = routers.NestedSimpleRouter(router, r'groups', lookup='study_group')
groups_router.register(r'members', StudyGroupMemberViewSet, basename='study-group-member')
groups_router.register(r'messages', StudyGroupMessageViewSet, basename='study-group-message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(topics_router.urls)),
    path('', include(groups_router.urls)),
]
