from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import MentorProfile, MentorshipRequest, Mentorship, MentorReview, MentorshipMessage
from .serializers import (
    MentorProfileSerializer, MentorshipRequestSerializer,
    MentorshipSerializer, MentorReviewSerializer, MentorshipMessageSerializer
)
from users.permissions import IsOwnerOrReadOnly

class MentorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = MentorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'expertise']
    ordering_fields = ['rating', 'review_count', 'years_of_experience']
    
    def get_queryset(self):
        queryset = MentorProfile.objects.filter(is_available=True)
        
        # Filter by skills
        skills = self.request.query_params.getlist('skill')
        if skills:
            queryset = queryset.filter(skills__id__in=skills).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            mentor_profile = MentorProfile.objects.get(user=request.user)
            serializer = MentorProfileSerializer(mentor_profile)
            return Response(serializer.data)
        except MentorProfile.DoesNotExist:
            return Response({'detail': 'Mentor profile not found.'}, status=status.HTTP_404_NOT_FOUND)

class MentorshipRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MentorshipRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Get requests sent by the user as mentee
        mentee_requests = MentorshipRequest.objects.filter(mentee=user)
        
        # Get requests received by the user as mentor
        try:
            mentor_profile = MentorProfile.objects.get(user=user)
            mentor_requests = MentorshipRequest.objects.filter(mentor=mentor_profile)
            return mentee_requests | mentor_requests
        except MentorProfile.DoesNotExist:
            return mentee_requests
    
    def perform_create(self, serializer):
        mentor_id = self.request.data.get('mentor_id')
        try:
            mentor = MentorProfile.objects.get(id=mentor_id)
            serializer.save(mentee=self.request.user, mentor=mentor)
        except MentorProfile.DoesNotExist:
            raise serializers.ValidationError({'mentor_id': 'Mentor profile not found.'})
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        mentorship_request = self.get_object()
        
        # Check if the user is the mentor
        try:
            mentor_profile = MentorProfile.objects.get(user=request.user)
            if mentorship_request.mentor != mentor_profile:
                return Response({'detail': 'You are not the mentor for this request.'}, status=status.HTTP_403_FORBIDDEN)
        except MentorProfile.DoesNotExist:
            return Response({'detail': 'You do not have a mentor profile.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the request is pending
        if mentorship_request.status != 'pending':
            return Response({'detail': 'This request has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update request status
        mentorship_request.status = 'accepted'
        mentorship_request.save()
        
        # Create mentorship
        mentorship = Mentorship.objects.create(
            mentee=mentorship_request.mentee,
            mentor=mentorship_request.mentor,
            goals=mentorship_request.message,
            start_date=timezone.now().date()
        )
        
        # Add skills to mentorship
        mentorship.skills.set(mentorship_request.skills_seeking.all())
        
        serializer = MentorshipSerializer(mentorship)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        mentorship_request = self.get_object()
        
        # Check if the user is the mentor
        try:
            mentor_profile = MentorProfile.objects.get(user=request.user)
            if mentorship_request.mentor != mentor_profile:
                return Response({'detail': 'You are not the mentor for this request.'}, status=status.HTTP_403_FORBIDDEN)
        except MentorProfile.DoesNotExist:
            return Response({'detail': 'You do not have a mentor profile.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the request is pending
        if mentorship_request.status != 'pending':
            return Response({'detail': 'This request has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update request status
        mentorship_request.status = 'rejected'
        mentorship_request.save()
        
        serializer = MentorshipRequestSerializer(mentorship_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        mentorship_request = self.get_object()
        
        # Check if the user is the mentee
        if mentorship_request.mentee != request.user:
            return Response({'detail': 'You are not the mentee for this request.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the request is pending
        if mentorship_request.status != 'pending':
            return Response({'detail': 'This request has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update request status
        mentorship_request.status = 'cancelled'
        mentorship_request.save()
        
        serializer = MentorshipRequestSerializer(mentorship_request)
        return Response(serializer.data)

class MentorshipViewSet(viewsets.ModelViewSet):
    serializer_class = MentorshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Get mentorships where the user is the mentee
        mentee_mentorships = Mentorship.objects.filter(mentee=user)
        
        # Get mentorships where the user is the mentor
        try:
            mentor_profile = MentorProfile.objects.get(user=user)
            mentor_mentorships = Mentorship.objects.filter(mentor=mentor_profile)
            return mentee_mentorships | mentor_mentorships
        except MentorProfile.DoesNotExist:
            return mentee_mentorships
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        mentorship = self.get_object()
        status_value = request.data.get('status')
        
        # Check if the user is part of the mentorship
        if mentorship.mentee != request.user and mentorship.mentor.user != request.user:
            return Response({'detail': 'You are not part of this mentorship.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Validate status
        if status_value not in dict(Mentorship.status.field.choices).keys():
            return Response({'detail': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status
        mentorship.status = status_value
        
        # If completed or terminated, set end date
        if status_value in ['completed', 'terminated']:
            mentorship.end_date = timezone.now().date()
        
        mentorship.save()
        
        serializer = MentorshipSerializer(mentorship)
        return Response(serializer.data)

class MentorReviewViewSet(viewsets.ModelViewSet):
    serializer_class = MentorReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MentorReview.objects.filter(mentorship__mentee=self.request.user)
    
    def perform_create(self, serializer):
        mentorship_id = self.request.data.get('mentorship_id')
        rating = self.request.data.get('rating')
        
        if not rating or not isinstance(rating, int) or rating &lt; 1 or rating > 5:
            raise serializers.ValidationError({'rating': 'Rating must be an integer between 1 and 5.'})
        
        try:
            mentorship = Mentorship.objects.get(id=mentorship_id, mentee=self.request.user)
        except Mentorship.DoesNotExist:
            raise serializers.ValidationError({'mentorship_id': 'Mentorship not found or you are not the mentee.'})
        
        # Check if review already exists
        if MentorReview.objects.filter(mentorship=mentorship).exists():
            raise serializers.ValidationError({'mentorship_id': 'You have already reviewed this mentorship.'})
        
        # Create review
        review = serializer.save(mentorship=mentorship)
        
        # Update mentor rating
        mentor = mentorship.mentor
        reviews = MentorReview.objects.filter(mentorship__mentor=mentor)
        total_rating = sum(r.rating for r in reviews)
        mentor.rating = total_rating / reviews.count()
        mentor.review_count = reviews.count()
        mentor.save()
        
        return review

class MentorshipMessageViewSet(viewsets.ModelViewSet):
    serializer_class = MentorshipMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        mentorship_id = self.kwargs.get('mentorship_pk')
        
        try:
            mentorship = Mentorship.objects.get(id=mentorship_id)
            
            # Check if the user is part of the mentorship
            if mentorship.mentee != user and mentorship.mentor.user != user:
                return MentorshipMessage.objects.none()
            
            return MentorshipMessage.objects.filter(mentorship=mentorship).order_by('created_at')
        except Mentorship.DoesNotExist:
            return MentorshipMessage.objects.none()
    
    def perform_create(self, serializer):
        mentorship_id = self.kwargs.get('mentorship_pk')
        
        try:
            mentorship = Mentorship.objects.get(id=mentorship_id)
            
            # Check if the user is part of the mentorship
            if mentorship.mentee != self.request.user and mentorship.mentor.user != self.request.user:
                raise serializers.ValidationError({'mentorship': 'You are not part of this mentorship.'})
            
            serializer.save(mentorship=mentorship, sender=self.request.user)
        except Mentorship.DoesNotExist:
            raise serializers.ValidationError({'mentorship': 'Mentorship not found.'})
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request, mentorship_pk=None):
        user = request.user
        
        try:
            mentorship = Mentorship.objects.get(id=mentorship_pk)
            
            # Check if the user is part of the mentorship
            if mentorship.mentee != user and mentorship.mentor.user != user:
                return Response({'detail': 'You are not part of this mentorship.'}, status=status.HTTP_403_FORBIDDEN)
            
            # Mark messages as read
            messages = MentorshipMessage.objects.filter(
                mentorship=mentorship,
                is_read=False
            ).exclude(sender=user)
            
            for message in messages:
                message.is_read = True
                message.save()
            
            return Response({'detail': f'Marked {messages.count()} messages as read.'})
        except Mentorship.DoesNotExist:
            return Response({'detail': 'Mentorship not found.'}, status=status.HTTP_404_NOT_FOUND)
