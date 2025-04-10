from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Education and career fields
    education_level = models.CharField(max_length=50, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    career_goals = models.TextField(blank=True)
    
    # Gamification fields
    xp_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    
    # Preferences
    is_mentor = models.BooleanField(default=False)
    is_mentee = models.BooleanField(default=True)
    receive_notifications = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=True)
    
    # Social links
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username
    
    def get_level_progress(self):
        """Calculate progress to next level"""
        # Example formula: 1000 * current_level = XP needed for next level
        next_level_xp = 1000 * self.level
        current_level_xp = 1000 * (self.level - 1)
        xp_for_current_level = self.xp_points - current_level_xp
        xp_needed_for_next_level = next_level_xp - current_level_xp
        return int((xp_for_current_level / xp_needed_for_next_level) * 100)

class Badge(models.Model):
    """Badges that users can earn"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    xp_reward = models.PositiveIntegerField(default=0)
    
    # Badge requirements
    required_level = models.PositiveIntegerField(default=0)
    required_courses = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    """Many-to-many relationship between users and badges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge')
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
