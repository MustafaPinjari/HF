from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0009_event_created_at_event_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='facility',
            name='type',
            field=models.CharField(
                choices=[
                    ('sports', 'Sports Facility'),
                    ('lab', 'Laboratory'),
                    ('transport', 'Transport'),
                    ('classroom', 'Classroom'),
                    ('other', 'Other')
                ],
                default='other',
                max_length=20
            ),
        ),
    ] 