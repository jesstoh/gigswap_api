# Generated by Django 3.2.2 on 2021-05-21 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gigs', '0006_alter_gig_expired_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gig',
            old_name='close',
            new_name='is_closed',
        ),
    ]
