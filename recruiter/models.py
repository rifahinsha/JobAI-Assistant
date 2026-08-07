from django.conf import settings
from django.db import models

from jobs.models import Job


class Application(models.Model):
    STATUS_APPLIED = 'applied'
    STATUS_REVIEWED = 'reviewed'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_APPLIED, 'Applied'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_SHORTLISTED, 'Shortlisted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    cover_note = models.TextField(blank=True)
    cv = models.FileField(upload_to='applications/cvs/%Y/%m/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant} -> {self.job}"