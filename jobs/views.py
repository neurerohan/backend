from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Company, JobListing, JobApplication, SavedJob
from .serializers import CompanySerializer, JobListingSerializer, JobApplicationSerializer, SavedJobSerializer
from users.permissions import IsOwnerOrReadOnly

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'industry', 'location']
    ordering_fields = ['name', 'size', 'created_at']

class JobListingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = JobListingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company__name', 'location']
    ordering_fields = ['posted_at', 'expires_at', 'salary_min', 'salary_max']
    
    def get_queryset(self):
        queryset = JobListing.objects.filter(is_active=True, expires_at__gte=timezone.now().date())
        
        # Filter by job type
        job_type = self.request.query_params.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        # Filter by experience level
        experience_level = self.request.query_params.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        # Filter by skills
        skills = self.request.query_params.getlist('skill')
        if skills:
            queryset = queryset.filter(skills__id__in=skills).distinct()
        
        # Filter by salary range
        min_salary = self.request.query_params.get('min_salary')
        if min_salary:
            queryset = queryset.filter(salary_min__gte=min_salary)
        
        max_salary = self.request.query_params.get('max_salary')
        if max_salary:
            queryset = queryset.filter(salary_max__lte=max_salary)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count
        instance.view_count += 1
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def save(self, request, pk=None):
        job_listing = self.get_object()
        user = request.user
        
        # Check if already saved
        if SavedJob.objects.filter(user=user, job_listing=job_listing).exists():
            return Response({'detail': 'Job already saved.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save job
        saved_job = SavedJob.objects.create(user=user, job_listing=job_listing)
        
        serializer = SavedJobSerializer(saved_job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def unsave(self, request, pk=None):
        job_listing = self.get_object()
        user = request.user
        
        # Check if saved
        try:
            saved_job = SavedJob.objects.get(user=user, job_listing=job_listing)
            saved_job.delete()
            return Response({'detail': 'Job removed from saved jobs.'})
        except SavedJob.DoesNotExist:
            return Response({'detail': 'Job not in saved jobs.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        job_listing = self.get_object()
        user = request.user
        
        # Check if already applied
        if JobApplication.objects.filter(user=user, job_listing=job_listing).exists():
            return Response({'detail': 'Already applied to this job.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate data
        cover_letter = request.data.get('cover_letter')
        resume = request.data.get('resume')
        
        if not cover_letter:
            return Response({'detail': 'Cover letter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not resume:
            return Response({'detail': 'Resume is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create application
        application = JobApplication.objects.create(
            user=user,
            job_listing=job_listing,
            cover_letter=cover_letter,
            resume=resume
        )
        
        # Increment application count
        job_listing.application_count += 1
        job_listing.save()
        
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        application = self.get_object()
        
        # Check if the user is the applicant
        if application.user != request.user:
            return Response({'detail': 'You are not the applicant.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the application can be withdrawn
        if application.status in ['rejected', 'withdrawn']:
            return Response({'detail': 'Application already withdrawn or rejected.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status
        application.status = 'withdrawn'
        application.save()
        
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data)

class SavedJobViewSet(viewsets.ModelViewSet):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)
