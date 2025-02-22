# Generated by Django 5.1.6 on 2025-02-20 16:26

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='manifesto',
            new_name='platform',
        ),
        migrations.RenameField(
            model_name='vote',
            old_name='timestamp',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='vote',
            old_name='voter',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='image',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='votes',
        ),
        migrations.AddField(
            model_name='candidate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='election',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='election',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together={('user', 'election')},
        ),
    ]
