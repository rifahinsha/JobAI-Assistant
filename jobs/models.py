from django.conf import settings
from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    about_role = models.TextField(
        blank=True, help_text="A short overview of the role and the team."
    )
    key_responsibilities = models.TextField(
        blank=True, help_text="What the person in this role will actually do, day to day."
    )
    required_skills = models.TextField(
        blank=True, help_text="Skills, tools, and experience required for this role."
    )
    what_we_offer = models.TextField(
        blank=True, help_text="Compensation, benefits, and perks offered for this role."
    )
    contact_email = models.EmailField(
        max_length=255, blank=True, help_text="Where applicants/queries about this job can be sent."
    )
    url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posted_jobs',
        help_text="Recruiter who posted this job. Blank for jobs posted via the admin panel.",
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company}"