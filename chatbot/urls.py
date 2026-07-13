from django.urls import path

from . import views

urlpatterns = [
    path("", views.root, name="chatbot_root"),
    path("chat", views.chat, name="chat"),
    path("reset", views.reset_chat, name="reset_chat"),
    path("history", views.get_history, name="get_history"),
    path("email-cover/analyze", views.email_analyze, name="email_analyze"),
    path("email-cover/cover-letter", views.email_cover_letter, name="email_cover_letter"),
    path("email-cover/cover-letter/pdf", views.email_cover_letter_pdf, name="email_cover_letter_pdf"),
]