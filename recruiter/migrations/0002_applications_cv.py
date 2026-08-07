from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruiter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='cv',
            field=models.FileField(blank=True, null=True, upload_to='applications/cvs/%Y/%m/'),
        ),
    ]