from rest_framework import serializers
from .models import MentorProfile, MentorshipRequest, Mentorship, MentorReview, MentorshipMessage
from users.serializers import UserProfileSerializer
from learning_paths.serializers import SkillSerializer

class MentorProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = MentorProfile
        fields = '__all__'
        read_only_fields = ('user', 'rating', 'review_count', 'created_at', 'updated_at')

class MentorshipRequestSerializer(serializers.ModelSerializer):
    mentee = UserProfileSerializer(read_only=True)
    mentor = MentorProfileSerializer(read_only=True)
    skills_seeking = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = MentorshipRequest
        fields = '__all__'
        read_only_fields = ('mentee', 'created_at', 'updated_at')

class MentorshipSerializer(serializers.ModelSerializer):
    mentee = UserProfileSerializer(read_only=True)
    mentor = MentorProfileSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Mentorship
        fields = '__all__'
        read_only_fields = ('mentee', 'mentor', 'created_at', 'updated_at')

class MentorReviewSerializer(serializers.ModelSerializer):
    mentorship = MentorshipSerializer(read_only=True)
    
    class Meta:
        model = MentorReview
        fields = '__all__'
        read_only_fields = ('mentorship', 'created_at', 'updated_at')

class MentorshipMessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = MentorshipMessage
        fields = '__all__'
        read_only_fields = ('mentorship', 'sender', 'created_at')
