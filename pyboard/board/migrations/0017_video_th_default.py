# Generated by Django 3.0.8 on 2020-08-11 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0016_auto_20200811_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='th_default',
            field=models.CharField(max_length=100, null=True),
        ),
    ]