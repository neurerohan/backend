from django.db import models
from users.models import User
from learning_paths.models import LearningPath, Skill

class ForumCategory(models.Model):
    """Categories for forum discussions"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='forum_categories/', blank=True, null=True)
    
    # Category statistics
    topic_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ForumTopic(models.Model):
    """Topics within forum categories"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    
    # Topic metadata
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    # Related entities
    learning_path = models.ForeignKey(LearningPath, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_topics')
    skills = models.ManyToManyField(Skill, related_name='forum_topics', blank=True)
    
    # Topic statistics
    view_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class ForumPost(models.Model):
    """Posts within forum topics"""
    content = models.TextField()
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    
    # Post metadata
    is_solution = models.BooleanField(default=False)
    
    # Post statistics
    like_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Post by {self.author.username} in {self.topic.title}"

class PostLike(models.Model):
    """Likes on forum posts"""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f"{self.user.username} likes {self.post}"

class StudyGroup(models.Model):
    """Study groups for collaborative learning"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Group details
    is_private = models.BooleanField(default=False)
    max_members = models.PositiveIntegerField(default=10)
    
    # Related entities
    learning_path = models.ForeignKey(LearningPath, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_groups')
    skills = models.ManyToManyField(Skill, related_name='study_groups', blank=True)
    
    # Group creator
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_study_groups')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class StudyGroupMember(models.Model):
    """Members of study groups"""
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_groups')
    
    # Member role
    role = models.CharField(max_length=50, choices=[
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ], default='member')
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('study_group', 'user')
    
    def __str__(self):
        return f"{self.user.username} in {self.study_group.name}"

class StudyGroupMessage(models.Model):
    """Messages in study groups"""
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_group_messages')
    
    # Message content
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.study_group.name}"
