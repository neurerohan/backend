from django.db import models
from users.models import User
from learning_paths.models import Skill

class Company(models.Model):
    """Companies that post job listings"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    website = models.URLField()
    logo = models.ImageField(upload_to='companies/', blank=True, null=True)
    
    # Company location
    location = models.CharField(max_length=100)
    
    # Company size
    size = models.CharField(max_length=50, choices=[
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001+', '1001+ employees'),
    ])
    
    # Company industry
    industry = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class JobListing(models.Model):
    """Job listings posted by companies"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_listings')
    
    # Job details
    job_type = models.CharField(max_length=50, choices=[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ])
    
    location = models.CharField(max_length=100)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    
    # Job requirements
    experience_level = models.CharField(max_length=50, choices=[
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive Level'),
    ])
    
    education_level = models.CharField(max_length=50, choices=[
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('none', 'No Requirement'),
    ])
    
    # Required skills
    skills = models.ManyToManyField(Skill, related_name='job_listings')
    
    # Job status
    is_active = models.BooleanField(default=True)
    
    # Job statistics
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0)
    
    posted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"

class JobApplication(models.Model):
    """Job applications submitted by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    
    # Application details
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    
    # Application status
    status = models.CharField(max_length=50, choices=[
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ], default='applied')
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'job_listing')
    
    def __str__(self):
        return f"{self.user.username} - {self.job_listing.title}"

class SavedJob(models.Model):
    """Jobs saved by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='saved_by')
    
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job_listing')
    
    def __str__(self):
        return f"{self.user.username} - {self.job_listing.title}"
