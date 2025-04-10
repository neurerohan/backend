from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'bio', 'avatar', 'date_of_birth', 'education_level', 
            'field_of_study', 'career_goals', 'xp_points', 'level',
            'is_mentor', 'is_mentee', 'linkedin_profile', 'github_profile',
            'personal_website', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'xp_points', 'level', 'created_at']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with limited fields"""
    
    full_name = serializers.SerializerMethodField()
    level_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'avatar', 
            'bio', 'xp_points', 'level', 'level_progress',
            'is_mentor', 'is_mentee', 'linkedin_profile', 
            'github_profile', 'personal_website'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_level_progress(self, obj):
        return obj.get_level_progress()

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 
            'first_name', 'last_name'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value
