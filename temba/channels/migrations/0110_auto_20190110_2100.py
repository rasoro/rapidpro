# Generated by Django 2.1.3 on 2019-01-10 21:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("channels", "0109_auto_20181212_1620")]

    operations = [
        migrations.RemoveField(model_name="channelsession", name="created_by"),
        migrations.RemoveField(model_name="channelsession", name="modified_by"),
    ]
