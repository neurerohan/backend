from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ResourceType, ResourceProvider, Resource, UserResource, ResourceRecommendation
from .serializers import (
    ResourceTypeSerializer, ResourceProviderSerializer, ResourceSerializer,
    UserResourceSerializer, ResourceRecommendationSerializer
)
from users.permissions import IsOwnerOrReadOnly

class ResourceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only endpoint for Resource Types."""
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    # Allow any authenticated user to read
    permission_classes = [permissions.IsAuthenticated]

class ResourceProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only endpoint for Resource Providers."""
    queryset = ResourceProvider.objects.all()
    serializer_class = ResourceProviderSerializer
    # Allow any authenticated user to read
    permission_classes = [permissions.IsAuthenticated]

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.select_related('resource_type', 'provider').all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'provider__name', 'resource_type__name']
    ordering_fields = ['title', 'created_at', 'view_count', 'bookmark_count', 'average_rating']
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        resource = self.get_object()
        user = request.user
        
        # Increment view count
        resource.view_count += 1
        resource.save()
        
        # Create or update user resource interaction
        user_resource, created = UserResource.objects.get_or_create(
            user=user,
            resource=resource
        )
        
        if not created:
            user_resource.viewed_at = timezone.now()
            user_resource.save()
        
        return Response({'detail': 'View recorded successfully.'})
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        resource = self.get_object()
        user = request.user
        bookmark = request.data.get('bookmark', True)
        
        # Create or update user resource interaction
        user_resource, created = UserResource.objects.get_or_create(
            user=user,
            resource=resource
        )
        
        # Update bookmark status
        if user_resource.is_bookmarked != bookmark:
            user_resource.is_bookmarked = bookmark
            user_resource.save()
            
            # Update bookmark count
            if bookmark:
                resource.bookmark_count += 1
            else:
                resource.bookmark_count = max(0, resource.bookmark_count - 1)
            
            resource.save()
        
        return Response({'detail': 'Bookmark updated successfully.'})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        resource = self.get_object()
        user = request.user
        rating = request.data.get('rating')
        
        if not rating or not isinstance(rating, int) or rating &lt; 1 or rating > 5:
            return Response({'detail': 'Rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update user resource interaction
        user_resource, created = UserResource.objects.get_or_create(
            user=user,
            resource=resource
        )
        
        # Update rating
        user_resource.rating = rating
        user_resource.save()
        
        # Update average rating
        rated_interactions = UserResource.objects.filter(resource=resource, rating__isnull=False)
        if rated_interactions.exists():
            total_rating = sum(i.rating for i in rated_interactions)
            resource.average_rating = total_rating / rated_interactions.count()
            resource.save()
        
        return Response({'detail': 'Rating submitted successfully.'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        resource = self.get_object()
        user = request.user
        completed = request.data.get('completed', True)
        
        # Create or update user resource interaction
        user_resource, created = UserResource.objects.get_or_create(
            user=user,
            resource=resource
        )
        
        # Update completion status
        if completed and not user_resource.is_completed:
            user_resource.is_completed = True
            user_resource.completed_at = timezone.now()
            user_resource.save()
            
            # Award XP to user (simple XP calculation)
            xp_points = min(50, resource.duration_minutes // 5)
            user.xp_points += xp_points
            
            # Level up if needed (simple level calculation)
            new_level = max(1, int(user.xp_points / 1000) + 1)
            if new_level > user.level:
                user.level = new_level
            
            user.save()
        elif not completed and user_resource.is_completed:
            user_resource.is_completed = False
            user_resource.completed_at = None
            user_resource.save()
        
        return Response({'detail': 'Completion status updated successfully.'})

class UserResourceViewSet(viewsets.ModelViewSet):
    serializer_class = UserResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # Also select related resource and its nested fields for efficiency
        return UserResource.objects.filter(user=self.request.user)\
               .select_related('resource__resource_type', 'resource__provider')
    
    @action(detail=False, methods=['get'])
    def bookmarked(self, request):
        bookmarked = self.get_queryset().filter(is_bookmarked=True)
        serializer = UserResourceSerializer(bookmarked, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        completed = self.get_queryset().filter(is_completed=True)
        serializer = UserResourceSerializer(completed, many=True)
        return Response(serializer.data)

class ResourceRecommendationViewSet(viewsets.ModelViewSet):
    """Endpoint for Resource Recommendations. Read for authenticated, Write for admin."""
    serializer_class = ResourceRecommendationSerializer
    # Default: Allow authenticated users to read
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Set permissions: Read for authenticated, Write for admin."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        learning_path_id = self.request.query_params.get('learning_path')
        path_step_id = self.request.query_params.get('path_step')
        
        if learning_path_id:
            return ResourceRecommendation.objects.filter(learning_path_id=learning_path_id)
        elif path_step_id:
            return ResourceRecommendation.objects.filter(path_step_id=path_step_id)
        
        return ResourceRecommendation.objects.none()
