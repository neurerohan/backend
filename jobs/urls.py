from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, JobListingViewSet, JobApplicationViewSet, SavedJobViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'listings', JobListingViewSet, basename='job-listing')
router.register(r'applications', JobApplicationViewSet, basename='job-application')
router.register(r'saved', SavedJobViewSet, basename='saved-job')

urlpatterns = [
    path('', include(router.urls)),
]
