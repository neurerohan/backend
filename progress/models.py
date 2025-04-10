from django.db import models
from users.models import User
from learning_paths.models import LearningPath, Step, Skill

class UserSkill(models.Model):
    """Skills acquired by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    # Skill proficiency
    proficiency = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ])
    
    # Skill metadata
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=100, blank=True)
    
    acquired_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'skill')
    
    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.proficiency})"

class UserStepProgress(models.Model):
    """User progress on individual path steps"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='step_progress')
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progress status
    status = models.CharField(max_length=50, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], default='not_started')
    
    # Progress metadata
    progress_percentage = models.PositiveIntegerField(default=0)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    
    # User feedback
    difficulty_rating = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'step')
    
    def __str__(self):
        return f"{self.user.username} - {self.step.title} ({self.status})"

class Achievement(models.Model):
    """Achievements that users can earn"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/')
    
    # Achievement categorization
    category = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ])
    
    # Achievement rewards
    xp_reward = models.PositiveIntegerField(default=0)
    
    # Achievement requirements
    required_paths_completed = models.PositiveIntegerField(default=0)
    required_skills = models.ManyToManyField(Skill, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class UserAchievement(models.Model):
    """Achievements earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"
