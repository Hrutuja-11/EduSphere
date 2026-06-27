from django.contrib import admin
from .models import Skill, Project, Certification, Achievement, Endorsement

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'verification_status', 'verified_by')
    list_filter = ('verification_status', 'verified_by')
    search_fields = ('title', 'student__user__username')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuing_organization', 'student', 'verification_status')
    list_filter = ('verification_status', 'issuing_organization')
    search_fields = ('name', 'student__user__username')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'student', 'verification_status')
    list_filter = ('category', 'verification_status')
    search_fields = ('title', 'student__user__username')

@admin.register(Endorsement)
class EndorsementAdmin(admin.ModelAdmin):
    list_display = ('student', 'faculty', 'relationship', 'created_at')
    list_filter = ('relationship', 'created_at')
