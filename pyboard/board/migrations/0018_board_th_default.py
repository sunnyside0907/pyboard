# Generated by Django 3.0.8 on 2020-08-11 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0017_video_th_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='th_default',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
