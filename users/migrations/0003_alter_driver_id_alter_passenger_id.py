# Generated by Django 4.0.4 on 2022-05-15 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_driver_user_alter_passenger_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='passenger',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]