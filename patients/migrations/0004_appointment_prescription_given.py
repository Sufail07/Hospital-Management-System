# Generated by Django 5.2.4 on 2025-07-23 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_remove_medicalhistory_treatment_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='prescription_given',
            field=models.BooleanField(default=False),
        ),
    ]
