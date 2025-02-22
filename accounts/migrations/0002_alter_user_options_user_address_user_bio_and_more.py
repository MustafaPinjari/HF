# Generated by Django 5.1.6 on 2025-02-20 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('can_view_dashboard', 'Can view dashboard'), ('can_manage_elections', 'Can manage elections'), ('can_manage_facilities', 'Can manage facilities'), ('can_handle_complaints', 'Can handle complaints')]},
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='emergency_contact',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='user',
            name='github_profile',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='linkedin_profile',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='department',
            field=models.CharField(choices=[('cs', 'Computer Science'), ('it', 'Information Technology'), ('ec', 'Electronics & Communication'), ('me', 'Mechanical Engineering'), ('ce', 'Civil Engineering'), ('admin', 'Administration')], max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('student', 'Student'), ('faculty', 'Faculty'), ('admin', 'Administrator'), ('staff', 'Staff')], max_length=20),
        ),
    ]
