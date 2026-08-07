from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_remove_profile_is_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('jobseeker', 'Job Seeker'), ('recruiter', 'Recruiter')], default='jobseeker', max_length=20),
        ),
    ]