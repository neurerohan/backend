from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import UserSkill, UserStepProgress, Achievement, UserAchievement
from .serializers import (
    UserSkillSerializer, UserStepProgressSerializer,
    AchievementSerializer, UserAchievementSerializer
)
from users.permissions import IsOwnerOrReadOnly
from learning_paths.models import PathStep

class UserSkillViewSet(viewsets.ModelViewSet):
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserStepProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserStepProgressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return UserStepProgress.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        progress = self.get_object()
        status_value = request.data.get('status')
        progress_percentage = request.data.get('progress_percentage')
        time_spent = request.data.get('time_spent_minutes', 0)
        
        # Update status
        if status_value:
            if status_value not in dict(UserStepProgress.status.field.choices).keys():
                return Response({'detail': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)
            
            progress.status = status_value
            
            # Update timestamps based on status
            if status_value == 'in_progress' and not progress.started_at:
                progress.started_at = timezone.now()
            elif status_value == 'completed' and not progress.completed_at:
                progress.completed_at = timezone.now()
                
                # Award XP to user
                user = progress.user
                user.xp_points += progress.path_step.xp_reward
                
                # Level up if needed (simple level calculation)
                new_level = max(1, int(user.xp_points / 1000) + 1)
                if new_level > user.level:
                    user.level = new_level
                
                user.save()
        
        # Update progress percentage
        if progress_percentage is not None:
            progress.progress_percentage = min(100, max(0, progress_percentage))
        
        # Update time spent
        if time_spent > 0:
            progress.time_spent_minutes += time_spent
        
        progress.save()
        serializer = UserStepProgressSerializer(progress)
        return Response(serializer.data)

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['title', 'category', 'difficulty', 'xp_reward']

class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user)
