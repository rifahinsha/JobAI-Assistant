from django.urls import path

from . import views

urlpatterns = [
    path("start", views.start_interview, name="interview_start"),
    path("answer", views.submit_answer, name="interview_answer"),
    path("reset", views.reset_interview, name="interview_reset"),
]
