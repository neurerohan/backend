from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    ForumCategory, ForumTopic, ForumPost, PostLike,
    StudyGroup, StudyGroupMember, StudyGroupMessage
)
from .serializers import (
    ForumCategorySerializer, ForumTopicSerializer, ForumPostSerializer,
    StudyGroupSerializer, StudyGroupMemberSerializer, StudyGroupMessageSerializer
)
from users.permissions import IsOwnerOrReadOnly

class ForumCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ForumCategory.objects.all()
    serializer_class = ForumCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'topic_count', 'post_count']

class ForumTopicViewSet(viewsets.ModelViewSet):
    serializer_class = ForumTopicSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'last_activity', 'view_count', 'reply_count']
    
    def get_queryset(self):
        queryset = ForumTopic.objects.all()
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by learning path
        learning_path_id = self.request.query_params.get('learning_path')
        if learning_path_id:
            queryset = queryset.filter(learning_path_id=learning_path_id)
        
        # Filter by skills
        skills = self.request.query_params.getlist('skill')
        if skills:
            queryset = queryset.filter(skills__id__in=skills).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        category_id = self.request.data.get('category_id')
        
        try:
            category = ForumCategory.objects.get(id=category_id)
        except ForumCategory.DoesNotExist:
            raise serializers.ValidationError({'category_id': 'Category not found.'})
        
        # Create topic
        topic = serializer.save(author=self.request.user, category=category)
        
        # Update category statistics
        category.topic_count += 1
        category.post_count += 1
        category.save()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count
        instance.view_count += 1
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class ForumPostViewSet(viewsets.ModelViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        topic_id = self.kwargs.get('topic_pk')
        return ForumPost.objects.filter(topic_id=topic_id).order_by('created_at')
    
    def perform_create(self, serializer):
        topic_id = self.kwargs.get('topic_pk')
        
        try:
            topic = ForumTopic.objects.get(id=topic_id)
        except ForumTopic.DoesNotExist:
            raise serializers.ValidationError({'topic': 'Topic not found.'})
        
        # Check if topic is locked
        if topic.is_locked:
            raise serializers.ValidationError({'topic': 'This topic is locked.'})
        
        # Create post
        post = serializer.save(author=self.request.user, topic=topic)
        
        # Update topic statistics
        topic.reply_count += 1
        topic.last_activity = timezone.now()
        topic.save()
        
        # Update category statistics
        category = topic.category
        category.post_count += 1
        category.save()
    
    @action(detail=True, methods=['post'])
    def like(self, request, topic_pk=None, pk=None):
        post = self.get_object()
        user = request.user
        
        # Check if already liked
        if PostLike.objects.filter(post=post, user=user).exists():
            return Response({'detail': 'Post already liked.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create like
        PostLike.objects.create(post=post, user=user)
        
        # Update post statistics
        post.like_count += 1
        post.save()
        
        return Response({'detail': 'Post liked successfully.'})
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, topic_pk=None, pk=None):
        post = self.get_object()
        user = request.user
        
        # Check if liked
        try:
            like = PostLike.objects.get(post=post, user=user)
            like.delete()
            
            # Update post statistics
            post.like_count = max(0, post.like_count - 1)
            post.save()
            
            return Response({'detail': 'Post unliked successfully.'})
        except PostLike.DoesNotExist:
            return Response({'detail': 'Post not liked.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_solution(self, request, topic_pk=None, pk=None):
        post = self.get_object()
        user = request.user
        
        # Check if user is the topic author
        if post.topic.author != user:
            return Response({'detail': 'Only the topic author can mark a solution.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Mark as solution
        post.is_solution = True
        post.save()
        
        # Award XP to post author
        post_author = post.author
        post_author.xp_points += 50  # Award XP for helpful answer
        
        # Level up if needed (simple level calculation)
        new_level = max(1, int(post_author.xp_points / 1000) + 1)
        if new_level > post_author.level:
            post_author.level = new_level
        
        post_author.save()
        
        return Response({'detail': 'Post marked as solution.'})

class StudyGroupViewSet(viewsets.ModelViewSet):
    serializer_class = StudyGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'creator__username']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Get public groups and groups the user is a member of
        public_groups = StudyGroup.objects.filter(is_private=False)
        user_groups = StudyGroup.objects.filter(members__user=user)
        
        return (public_groups | user_groups).distinct()
    
    def perform_create(self, serializer):
        group = serializer.save(creator=self.request.user)
        
        # Add creator as admin member
        StudyGroupMember.objects.create(
            study_group=group,
            user=self.request.user,
            role='admin'
        )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        study_group = self.get_object()
        user = request.user
        
        # Check if already a member
        if StudyGroupMember.objects.filter(study_group=study_group, user=user).exists():
            return Response({'detail': 'Already a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if group is full
        if study_group.members.count() >= study_group.max_members:
            return Response({'detail': 'Group is full.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if group is private
        if study_group.is_private:
            return Response({'detail': 'Cannot join private group directly. Request to join instead.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Join group
        member = StudyGroupMember.objects.create(
            study_group=study_group,
            user=user,
            role='member'
        )
        
        serializer = StudyGroupMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        study_group = self.get_object()
        user = request.user
        
        # Check if a member
        try:
            member = StudyGroupMember.objects.get(study_group=study_group, user=user)
            
            # Check if the user is the creator/admin
            if member.role == 'admin' and study_group.creator == user:
                return Response({'detail': 'Group creator cannot leave. Transfer ownership or delete the group.'}, status=status.HTTP_400_BAD_REQUEST)
            
            member.delete()
            return Response({'detail': 'Left the group successfully.'})
        except StudyGroupMember.DoesNotExist:
            return Response({'detail': 'Not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

class StudyGroupMemberViewSet(viewsets.ModelViewSet):
    serializer_class = StudyGroupMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        study_group_id = self.kwargs.get('study_group_pk')
        return StudyGroupMember.objects.filter(study_group_id=study_group_id)
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, study_group_pk=None, pk=None):
        member = self.get_object()
        user = request.user
        role = request.data.get('role')
        
        # Check if the user is an admin of the group
        try:
            user_member = StudyGroupMember.objects.get(study_group_id=study_group_pk, user=user)
            if user_member.role != 'admin':
                return Response({'detail': 'Only group admins can change roles.'}, status=status.HTTP_403_FORBIDDEN)
        except StudyGroupMember.DoesNotExist:
            return Response({'detail': 'You are not a member of this group.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Validate role
        if role not in dict(StudyGroupMember.role.field.choices).keys():
            return Response({'detail': 'Invalid role value.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cannot change role of the group creator
        if member.user == member.study_group.creator and role != 'admin':
            return Response({'detail': 'Cannot change the role of the group creator.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update role
        member.role = role
        member.save()
        
        serializer = StudyGroupMemberSerializer(member)
        return Response(serializer.data)

class StudyGroupMessageViewSet(viewsets.ModelViewSet):
    serializer_class = StudyGroupMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        study_group_id = self.kwargs.get('study_group_pk')
        
        # Check if user is a member of the group
        user = self.request.user
        if not StudyGroupMember.objects.filter(study_group_id=study_group_id, user=user).exists():
            return StudyGroupMessage.objects.none()
        
        return StudyGroupMessage.objects.filter(study_group_id=study_group_id).order_by('created_at')
    
    def perform_create(self, serializer):
        study_group_id = self.kwargs.get('study_group_pk')
        user = self.request.user
        
        # Check if user is a member of the group
        if not StudyGroupMember.objects.filter(study_group_id=study_group_id, user=user).exists():
            raise serializers.ValidationError({'detail': 'You are not a member of this group.'})
        
        serializer.save(study_group_id=study_group_id, sender=user)
