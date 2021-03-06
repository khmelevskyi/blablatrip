# Generated by Django 4.0.4 on 2022-05-15 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'City',
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_of_places', models.PositiveIntegerField()),
                ('start_date_and_time', models.DateTimeField()),
                ('description', models.TextField(blank=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.driver')),
                ('end_city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='End_city', to='trips.city')),
                ('passengers', models.ManyToManyField(to='users.passenger')),
                ('start_city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Start_city', to='trips.city')),
            ],
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trips.country'),
        ),
    ]
