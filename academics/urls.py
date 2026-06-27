from django.urls import path
from . import views

urlpatterns = [
    path('transcript/<str:username>/', views.academic_transcript, name='transcript'),
    path('mark-attendance/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    path('upload-grades/<int:course_id>/', views.upload_grades, name='upload_grades'),
    path('academics/history/', views.student_academics, name='student_academics'),
    path('academics/timetable/add/', views.add_timetable_entry, name='add_timetable_entry'),
    path('academics/timetable/delete/<int:entry_id>/', views.delete_timetable_entry, name='delete_timetable_entry'),
    path('academics/course/add/', views.add_course, name='add_course'),
    path('academics/course/<int:course_id>/assign/', views.assign_faculty, name='assign_faculty'),
]
