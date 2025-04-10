from django.db import models
from users.models import User
from learning_paths.models import Skill

class MentorProfile(models.Model):
    """Profile for mentors"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    
    # Mentor details
    bio = models.TextField()
    expertise = models.TextField()
    years_of_experience = models.PositiveIntegerField()
    
    # Mentor availability
    is_available = models.BooleanField(default=True)
    max_mentees = models.PositiveIntegerField(default=5)
    
    # Mentor skills
    skills = models.ManyToManyField(Skill, related_name='mentors')
    
    # Mentor statistics
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Mentor: {self.user.username}"

class MentorshipRequest(models.Model):
    """Mentorship requests from mentees to mentors"""
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorship_requests')
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='mentorship_requests')
    
    # Request details
    message = models.TextField()
    skills_seeking = models.ManyToManyField(Skill, related_name='mentorship_requests')
    
    # Request status
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.mentee.username} -> {self.mentor.user.username} ({self.status})"

class Mentorship(models.Model):
    """Active mentorship relationships"""
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorships')
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='mentorships')
    
    # Mentorship details
    goals = models.TextField()
    skills = models.ManyToManyField(Skill, related_name='mentorships')
    
    # Mentorship status
    status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ], default='active')
    
    # Mentorship duration
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('mentee', 'mentor')
    
    def __str__(self):
        return f"{self.mentee.username} mentored by {self.mentor.user.username}"

class MentorReview(models.Model):
    """Reviews for mentors from mentees"""
    mentorship = models.ForeignKey(Mentorship, on_delete=models.CASCADE, related_name='reviews')
    
    # Review details
    rating = models.PositiveIntegerField()
    review = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('mentorship',)
    
    def __str__(self):
        return f"Review for {self.mentorship.mentor.user.username} by {self.mentorship.mentee.username}"

class MentorshipMessage(models.Model):
    """Messages between mentors and mentees"""
    mentorship = models.ForeignKey(Mentorship, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_mentorship_messages')
    
    # Message content
    content = models.TextField()
    
    # Message status
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.mentorship}"
