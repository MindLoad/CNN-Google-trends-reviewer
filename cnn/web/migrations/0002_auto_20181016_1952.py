# Generated by Django 2.1.2 on 2018-10-16 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cnnnews',
            options={'ordering': ['-created'], 'verbose_name_plural': 'CNN News'},
        ),
        migrations.AlterModelOptions(
            name='googletrendsatom',
            options={'ordering': ['-updated'], 'verbose_name_plural': 'Google Trends'},
        ),
    ]