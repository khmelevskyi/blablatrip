# Generated by Django 4.0.4 on 2022-05-18 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0005_trip_start_date_time'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='trip',
            name='start_date_time',
        ),
    ]
