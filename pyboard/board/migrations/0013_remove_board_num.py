# Generated by Django 3.0.8 on 2020-08-07 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0012_auto_20200807_1342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='num',
        ),
    ]
