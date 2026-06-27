from django.contrib import admin
from .models import Company, JobPosting, JobApplication

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'website')
    search_fields = ('name', 'industry')

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'min_cgpa', 'application_deadline', 'is_active')
    list_filter = ('job_type', 'is_active', 'company')
    search_fields = ('title', 'company__name')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job_posting', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__user__username', 'job_posting__title', 'job_posting__company__name')
