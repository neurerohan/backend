from django.db import models
from users.models import User
from learning_paths.models import LearningPath, Step, Skill

class ResourceType(models.Model):
    """Types of resources (e.g., video, article, course)"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='resource_types/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class ResourceProvider(models.Model):
    """Resource providers (e.g., Udemy, Coursera, YouTube)"""
    name = models.CharField(max_length=100)
    website = models.URLField()
    logo = models.ImageField(upload_to='resource_providers/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Resource(models.Model):
    """Educational resources for learning paths"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()
    thumbnail = models.ImageField(upload_to='resources/', blank=True, null=True)
    
    # Resource categorization
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    provider = models.ForeignKey(ResourceProvider, on_delete=models.CASCADE)
    
    # Resource metadata
    duration_minutes = models.PositiveIntegerField(default=0)
    difficulty = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    is_free = models.BooleanField(default=True)
    
    # Related entities
    skills = models.ManyToManyField(Skill, related_name='resources')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_resources')
    
    # Resource statistics
    view_count = models.PositiveIntegerField(default=0)
    bookmark_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class UserResource(models.Model):
    """User interactions with resources"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='user_interactions')
    
    # User interaction
    is_bookmarked = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    viewed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'resource')
    
    def __str__(self):
        return f"{self.user.username} - {self.resource.title}"

class ResourceRecommendation(models.Model):
    """Resource recommendations for learning paths or steps"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='recommendations')
    
    # Recommendation target (either learning path or path step)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, null=True, blank=True, related_name='recommended_resources')
    path_step = models.ForeignKey(Step, on_delete=models.CASCADE, null=True, blank=True, related_name='recommended_resources')
    
    # Recommendation metadata
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        target = self.learning_path.title if self.learning_path else self.path_step.title
        return f"{self.resource.title} - {target}"
