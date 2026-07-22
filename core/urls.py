from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('admin_panel.urls')),
    path('', include('authentication.urls')),
    path('jobs-api/', include('jobs.urls')),
    path('chatbot-api/', include('chatbot.urls')),
    path('ats-api/', include('ats_analyser.urls')),
    path('interview-api/', include('mock_interview.urls')),
<<<<<<< HEAD
    path('resume-builder/', include('resume_builder.urls')),
=======
    path('roadmap-api/', include('career_roadmap.urls')),
>>>>>>> cecf14376a67ce66d90c4661efa1c4c2052ee7f0
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)