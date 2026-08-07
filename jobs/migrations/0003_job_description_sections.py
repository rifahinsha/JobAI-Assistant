from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_job_posted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='about_role',
            field=models.TextField(blank=True, help_text='A short overview of the role and the team.'),
        ),
        migrations.AddField(
            model_name='job',
            name='key_responsibilities',
            field=models.TextField(blank=True, help_text='What the person in this role will actually do, day to day.'),
        ),
        migrations.AddField(
            model_name='job',
            name='required_skills',
            field=models.TextField(blank=True, help_text='Skills, tools, and experience required for this role.'),
        ),
        migrations.AddField(
            model_name='job',
            name='what_we_offer',
            field=models.TextField(blank=True, help_text='Compensation, benefits, and perks offered for this role.'),
        ),
        migrations.AddField(
            model_name='job',
            name='contact_email',
            field=models.EmailField(blank=True, help_text='Where applicants/queries about this job can be sent.', max_length=255),
        ),
    ]