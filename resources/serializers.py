from rest_framework import serializers
from .models import ResourceType, ResourceProvider, Resource, UserResource, ResourceRecommendation

class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceType
        fields = '__all__'

class ResourceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceProvider
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    resource_type = ResourceTypeSerializer(read_only=True)
    provider = ResourceProviderSerializer(read_only=True)
    
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ('added_by', 'view_count', 'bookmark_count', 'average_rating')

class UserResourceSerializer(serializers.ModelSerializer):
    resource = ResourceSerializer(read_only=True)
    
    class Meta:
        model = UserResource
        fields = '__all__'
        read_only_fields = ('user', 'viewed_at', 'completed_at')

class ResourceRecommendationSerializer(serializers.ModelSerializer):
    resource = ResourceSerializer(read_only=True)
    
    class Meta:
        model = ResourceRecommendation
        fields = '__all__'
