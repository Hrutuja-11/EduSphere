from django.urls import path
from . import views

urlpatterns = [
    path('portfolio/manage/', views.manage_portfolio, name='manage_portfolio'),

    path('portfolio/add-project/', views.add_project, name='add_project'),
    path('portfolio/edit-project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('portfolio/delete-project/<int:project_id>/', views.delete_project, name='delete_project'),

    path('portfolio/add-certification/', views.add_certification, name='add_certification'),
    path('portfolio/edit-certification/<int:cert_id>/', views.edit_certification, name='edit_certification'),
    path('portfolio/delete-certification/<int:cert_id>/', views.delete_certification, name='delete_certification'),

    path('portfolio/add-achievement/', views.add_achievement, name='add_achievement'),
    path('portfolio/edit-achievement/<int:ach_id>/', views.edit_achievement, name='edit_achievement'),
    path('portfolio/delete-achievement/<int:ach_id>/', views.delete_achievement, name='delete_achievement'),

    path('portfolio/update-skills/', views.update_skills, name='update_skills'),
    path('portfolio/update-contact/', views.update_contact_info, name='update_contact_info'),
    path('portfolio/verify/<str:item_type>/<int:item_id>/<str:action>/', views.verify_item, name='verify_item'),
    path('portfolio/endorse/<int:student_id>/', views.add_endorsement, name='add_endorsement'),

    # Hamesha LAST me rakho
    path('portfolio/<str:username>/', views.public_portfolio, name='public_portfolio'),
]
