# Generated by Django 3.0.8 on 2020-08-12 02:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0019_auto_20200812_1108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='th_high',
        ),
    ]
