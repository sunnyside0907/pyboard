# Generated by Django 3.0.8 on 2020-08-06 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0010_auto_20200806_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='video_url',
            field=models.CharField(default='insert', max_length=100),
        ),
    ]
