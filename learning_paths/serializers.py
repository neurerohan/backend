from rest_framework import serializers
from .models import Skill, LearningPath, Step, UserLearningPath
from users.serializers import UserPublicProfileSerializer

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class StepSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Step
        fields = '__all__'

class LearningPathSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)
    creator = UserPublicProfileSerializer(read_only=True)
    
    class Meta:
        model = LearningPath
        fields = '__all__'
        read_only_fields = ('creator', 'enrolled_count', 'completion_count', 'average_rating')
    
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class UserLearningPathSerializer(serializers.ModelSerializer):
    learning_path = LearningPathSerializer(read_only=True)
    
    class Meta:
        model = UserLearningPath
        fields = '__all__'
        read_only_fields = ('user', 'progress_percentage', 'current_step', 'enrolled_at', 'updated_at', 'completed_at')
