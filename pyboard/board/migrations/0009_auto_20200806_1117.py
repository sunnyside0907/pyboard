# Generated by Django 3.0.8 on 2020-08-06 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0008_auto_20200806_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='video_url',
            field=models.URLField(max_length=100, null=True),
        ),
    ]
