from django.urls import path

from . import views

app_name = "resume_builder"

urlpatterns = [
    path("", views.resume_builder, name="resume_builder"),
    path("download/", views.download_resume_pdf, name="download_resume_pdf"),
]