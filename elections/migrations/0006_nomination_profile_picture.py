# Generated by Django 5.1.6 on 2025-02-21 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0005_alter_nomination_achievements_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='nomination',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='candidate_profiles/'),
        ),
    ]
