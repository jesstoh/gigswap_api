# Generated by Django 3.2.2 on 2021-05-19 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gigs', '0003_gig_duration_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gig',
            name='expired_at',
        ),
    ]
