from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Skill, LearningPath, PathStep, UserLearningPath
from .serializers import SkillSerializer, LearningPathSerializer, PathStepSerializer, UserLearningPathSerializer
from users.permissions import IsOwnerOrReadOnly

class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'category', 'level']

class LearningPathViewSet(viewsets.ModelViewSet):
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['title', 'created_at', 'enrolled_count', 'average_rating']
    
    def get_queryset(self):
        user = self.request.user
        # Show public paths and private paths created by the user
        return LearningPath.objects.filter(is_public=True) | LearningPath.objects.filter(creator=user)
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        learning_path = self.get_object()
        user = request.user
        
        # Check if already enrolled
        if UserLearningPath.objects.filter(user=user, learning_path=learning_path).exists():
            return Response({'detail': 'Already enrolled in this learning path.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create enrollment
        enrollment = UserLearningPath.objects.create(
            user=user,
            learning_path=learning_path,
            status='enrolled'
        )
        
        # Update enrollment count
        learning_path.enrolled_count += 1
        learning_path.save()
        
        serializer = UserLearningPathSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        learning_path = self.get_object()
        user = request.user
        rating = request.data.get('rating')
        review = request.data.get('review', '')
        
        if not rating or not isinstance(rating, int) or rating &lt; 1 or rating > 5:
            return Response({'detail': 'Rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user enrollment
        try:
            enrollment = UserLearningPath.objects.get(user=user, learning_path=learning_path)
        except UserLearningPath.DoesNotExist:
            return Response({'detail': 'You must be enrolled to rate this learning path.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update rating and review
        enrollment.rating = rating
        enrollment.review = review
        enrollment.save()
        
        # Update average rating
        rated_enrollments = UserLearningPath.objects.filter(learning_path=learning_path, rating__isnull=False)
        if rated_enrollments.exists():
            total_rating = sum(e.rating for e in rated_enrollments)
            learning_path.average_rating = total_rating / rated_enrollments.count()
            learning_path.save()
        
        return Response({'detail': 'Rating submitted successfully.'})

class PathStepViewSet(viewsets.ModelViewSet):
    serializer_class = PathStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        learning_path_id = self.kwargs.get('learning_path_pk')
        return PathStep.objects.filter(learning_path_id=learning_path_id).order_by('order')
    
    def perform_create(self, serializer):
        learning_path_id = self.kwargs.get('learning_path_pk')
        learning_path = LearningPath.objects.get(id=learning_path_id)
        
        # Check if user is the creator of the learning path
        if learning_path.creator != self.request.user:
            self.permission_denied(self.request, message='You do not have permission to add steps to this learning path.')
        
        serializer.save(learning_path_id=learning_path_id)

class UserLearningPathViewSet(viewsets.ModelViewSet):
    serializer_class = UserLearningPathSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return UserLearningPath.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        enrollment = self.get_object()
        step_id = request.data.get('step_id')
        completed = request.data.get('completed', False)
        
        if not step_id:
            return Response({'detail': 'Step ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            step = PathStep.objects.get(id=step_id, learning_path=enrollment.learning_path)
        except PathStep.DoesNotExist:
            return Response({'detail': 'Step not found in this learning path.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Update current step
        enrollment.current_step = step
        
        # If step is completed, update progress percentage
        if completed:
            total_steps = enrollment.learning_path.steps.count()
            completed_steps = request.data.get('completed_steps', 0)
            
            if total_steps > 0:
                enrollment.progress_percentage = min(100, int((completed_steps / total_steps) * 100))
            
            # If all steps completed, mark as completed
            if enrollment.progress_percentage == 100:
                enrollment.status = 'completed'
                enrollment.completed_at = timezone.now()
                
                # Update completion count for learning path
                learning_path = enrollment.learning_path
                learning_path.completion_count += 1
                learning_path.save()
                
                # Award XP to user
                user = enrollment.user
                user.xp_points += learning_path.xp_reward
                
                # Level up if needed (simple level calculation)
                new_level = max(1, int(user.xp_points / 1000) + 1)
                if new_level > user.level:
                    user.level = new_level
                
                user.save()
            else:
                enrollment.status = 'in_progress'
        
        enrollment.save()
        
        serializer = UserLearningPathSerializer(enrollment)
        return Response(serializer.data)
