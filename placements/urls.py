from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.browse_jobs, name='browse_jobs'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('placements/manage/', views.manage_placements, name='manage_placements'),
    path('placements/post-job/', views.post_job, name='post_job'),
    path('placements/application/<int:app_id>/update/<str:status>/', views.update_application_status, name='update_application_status'),
]
