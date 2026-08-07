from django.urls import path

from . import views

app_name = 'recruiter'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('jobs/<int:pk>/applicants/', views.applicants, name='applicants'),
    path('applications/<int:pk>/status/', views.update_application_status, name='update_application_status'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('shortlisted/', views.shortlisted_candidates, name='shortlisted_candidates'),
]