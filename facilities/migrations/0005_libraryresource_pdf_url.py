# Generated by Django 5.1.6 on 2025-02-21 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0004_course_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryresource',
            name='pdf_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
