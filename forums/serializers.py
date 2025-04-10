from rest_framework import serializers
from .models import (
    ForumCategory, ForumTopic, ForumPost, PostLike,
    StudyGroup, StudyGroupMember, StudyGroupMessage
)
from users.serializers import UserPublicProfileSerializer
from learning_paths.serializers import LearningPathSerializer, SkillSerializer

class ForumCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumCategory
        fields = '__all__'
        read_only_fields = ('topic_count', 'post_count', 'created_at', 'updated_at')

class ForumTopicSerializer(serializers.ModelSerializer):
    author = UserPublicProfileSerializer(read_only=True)
    category = ForumCategorySerializer(read_only=True)
    learning_path = LearningPathSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = ForumTopic
        fields = '__all__'
        read_only_fields = ('author', 'view_count', 'reply_count', 'created_at', 'updated_at', 'last_activity')

class ForumPostSerializer(serializers.ModelSerializer):
    author = UserPublicProfileSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumPost
        fields = '__all__'
        read_only_fields = ('author', 'like_count', 'created_at', 'updated_at')
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False

class StudyGroupSerializer(serializers.ModelSerializer):
    creator = UserPublicProfileSerializer(read_only=True)
    learning_path = LearningPathSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyGroup
        fields = '__all__'
        read_only_fields = ('creator', 'created_at', 'updated_at')
    
    def get_member_count(self, obj):
        return obj.members.count()

class StudyGroupMemberSerializer(serializers.ModelSerializer):
    user = UserPublicProfileSerializer(read_only=True)
    study_group = StudyGroupSerializer(read_only=True)
    
    class Meta:
        model = StudyGroupMember
        fields = '__all__'
        read_only_fields = ('joined_at',)

class StudyGroupMessageSerializer(serializers.ModelSerializer):
    sender = UserPublicProfileSerializer(read_only=True)
    
    class Meta:
        model = StudyGroupMessage
        fields = '__all__'
        read_only_fields = ('study_group', 'sender', 'created_at')
