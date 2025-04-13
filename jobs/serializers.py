from rest_framework import serializers
from .models import Company, JobListing, JobApplication, SavedJob
from users.serializers import UserProfileSerializer
from learning_paths.serializers import SkillSerializer

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class JobListingSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    is_saved = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = JobListing
        fields = '__all__'
        read_only_fields = ('view_count', 'application_count', 'posted_at', 'updated_at')
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedJob.objects.filter(user=request.user, job_listing=obj).exists()
        return False
    
    def get_has_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobApplication.objects.filter(user=request.user, job_listing=obj).exists()
        return False

class JobApplicationSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    job_listing = JobListingSerializer(read_only=True)
    
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ('user', 'applied_at', 'updated_at')

class SavedJobSerializer(serializers.ModelSerializer):
    job_listing = JobListingSerializer(read_only=True)
    
    class Meta:
        model = SavedJob
        fields = '__all__'
        read_only_fields = ('user', 'saved_at')
