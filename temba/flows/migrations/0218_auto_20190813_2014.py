# Generated by Django 2.2.4 on 2019-08-13 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("flows", "0217_auto_20190926_1500")]

    operations = [
        # make FlowSession.uuid non-NULL and unique
        migrations.AlterField(model_name="flowsession", name="uuid", field=models.UUIDField(unique=True)),
        # make FlowRun.status non-NULL
        migrations.AlterField(
            model_name="flowrun",
            name="status",
            field=models.CharField(
                choices=[
                    ("A", "Active"),
                    ("W", "Waiting"),
                    ("C", "Completed"),
                    ("I", "Interrupted"),
                    ("X", "Expired"),
                    ("F", "Failed"),
                ],
                max_length=1,
            ),
        ),
    ]
