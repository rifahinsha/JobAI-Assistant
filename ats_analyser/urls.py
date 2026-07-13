from django.urls import path

from . import views

urlpatterns = [
    path("", views.root, name="ats_root"),
    path("health", views.health, name="ats_health"),
    path("analyze/text", views.analyze_text, name="analyze_text"),
    path("analyze/files", views.analyze_files, name="analyze_files"),
    path("analyze/mixed", views.analyze_mixed, name="analyze_mixed"),
]