# Generated by Django 5.1.6 on 2025-02-22 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_user_class_year_user_division_user_prn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='division',
            field=models.CharField(blank=True, choices=[('A', '01'), ('B', '02'), ('C', '03')], max_length=1, null=True),
        ),
    ]
