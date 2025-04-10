from rest_framework import serializers
from .models import UserSkill, UserStepProgress, Achievement, UserAchievement
from learning_paths.serializers import SkillSerializer, StepSerializer

class UserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    
    class Meta:
        model = UserSkill
        fields = '__all__'
        read_only_fields = ('user', 'is_verified', 'verification_method', 'acquired_at', 'updated_at')

class UserStepProgressSerializer(serializers.ModelSerializer):
    step = StepSerializer(read_only=True)
    
    class Meta:
        model = UserStepProgress
        fields = '__all__'
        read_only_fields = ('user', 'started_at', 'completed_at', 'updated_at')

class AchievementSerializer(serializers.ModelSerializer):
    required_skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Achievement
        fields = '__all__'

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = '__all__'
        read_only_fields = ('user', 'earned_at')
