from django.urls import path

from . import views

urlpatterns = [
    path("api/jobs", views.get_jobs, name="get_jobs"),
]