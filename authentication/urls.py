from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name="landing"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('profile/', views.profile, name="profile"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('save_job/', views.save_job, name="save_job"),
    path('saved_jobs/', views.saved_jobs, name="saved_jobs"),
    path('unsave_job/', views.unsave_job, name="unsave_job"),
    path('posted_jobs', views.posted_jobs, name="posted_jobs"),
    path('chatbot/', views.chatbot, name="chatbot"),
    path('ats_analyzer/', views.ats_analyzer, name="ats_analyzer"),
    path('mock_interview/', views.mock_interview, name="mock_interview"),
    path('job_openings/', views.job_openings, name='job_openings'),
    path('email_cv/',views.email_cv,name="email_cv"),
]