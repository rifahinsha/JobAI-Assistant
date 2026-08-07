import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='posted_by',
            field=models.ForeignKey(blank=True, help_text='Recruiter who posted this job. Blank for jobs posted via the admin panel.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posted_jobs', to=settings.AUTH_USER_MODEL),
        ),
    ]