# Generated by Django 3.1.14 on 2022-10-08 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon_entities', '0003_auto_20221008_1348'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pokemon',
            old_name='photo',
            new_name='image',
        ),
    ]
