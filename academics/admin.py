from django.contrib import admin
from .models import Department, Course, CourseEnrollment, AttendanceRecord, ExamResult

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credits', 'semester')
    list_filter = ('department', 'semester')
    search_fields = ('code', 'name')

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'grade', 'attendance_percentage')
    list_filter = ('semester', 'course')
    search_fields = ('student__user__username', 'course__name')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'date', 'status')
    list_filter = ('date', 'status', 'enrollment__course')

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'assessment_name', 'max_marks', 'marks_obtained')
    list_filter = ('assessment_name',)
