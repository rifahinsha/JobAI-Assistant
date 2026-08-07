from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_profile_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='company_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='profile',
            name='company_website',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]