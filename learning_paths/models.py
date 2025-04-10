from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class Skill(models.Model):
    """Model for skills that can be learned in learning paths"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    """Model for categorizing learning paths"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class LearningPath(models.Model):
    """Model for learning paths"""
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    estimated_duration = models.PositiveIntegerField(help_text="Duration in hours")
    xp_reward = models.PositiveIntegerField(default=100)
    image = models.ImageField(upload_to='learning_paths/', null=True, blank=True)
    
    # Relationships
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_paths')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='learning_paths')
    skills = models.ManyToManyField(Skill, related_name='learning_paths')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    @property
    def enrolled_count(self):
        return self.user_paths.count()
    
    @property
    def completion_count(self):
        return self.user_paths.filter(is_completed=True).count()

class Step(models.Model):
    """Model for steps within a learning path"""
    STEP_TYPE_CHOICES = [
        ('lesson', 'Lesson'),
        ('quiz', 'Quiz'),
        ('project', 'Project'),
        ('assignment', 'Assignment'),
    ]
    
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES, default='lesson')
    content = models.TextField(blank=True)
    estimated_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    xp_reward = models.PositiveIntegerField(default=10)
    
    class Meta:
        ordering = ['order']
        unique_together = ['learning_path', 'order']
    
    def __str__(self):
        return f"{self.learning_path.title} - Step {self.order}: {self.title}"

class UserLearningPath(models.Model):
    """Model for tracking user progress in learning paths"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='user_paths')
    current_step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_users')
    progress = models.PositiveIntegerField(default=0)  # Percentage of completion
    is_completed = models.BooleanField(default=False)
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'learning_path']
    
    def __str__(self):
        return f"{self.user.username} - {self.learning_path.title}"

class UserStepProgress(models.Model):
    """Model for tracking user progress in individual steps"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='step_progress')
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'step']
    
    def __str__(self):
        return f"{self.user.username} - {self.step.title} - {self.status}"
