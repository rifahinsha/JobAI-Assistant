from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    phone_number = models.CharField(max_length=15, blank=True)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class SavedJob(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_jobs")
    adzuna_id=models.CharField(max_length=50)
    title=models.CharField(max_length=255)
    company=models.CharField(max_length=255,blank=True)
    location=models.CharField(max_length=255,blank=True)
    description=models.TextField(blank=True)
    salary_max=models.FloatField(null=True,blank=True)
    salary_min=models.FloatField(null=True,blank=True)
    url=models.URLField(max_length=500)
    created=models.CharField(max_length=50,blank=True)
    saved_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=("user","adzuna_id")
    
    def __str__(self):
        return f"{self.title} - {self.user}"