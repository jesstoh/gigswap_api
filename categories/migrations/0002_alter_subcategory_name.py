# Generated by Django 3.2.2 on 2021-05-20 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcategory',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
