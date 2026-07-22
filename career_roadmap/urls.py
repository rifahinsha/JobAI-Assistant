from django.urls import path

from . import views

urlpatterns = [
    path("generate", views.generate, name="roadmap_generate"),
    path("download", views.download_pdf, name="roadmap_download"),
]
