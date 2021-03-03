# Generated by Django 2.2.4 on 2019-10-17 15:54

from django.db import migrations
from django.db.models import F, Value
from django.db.models.functions import Concat


def recipients_to_urns(apps, schema_editor):
    AirtimeTransfer = apps.get_model("airtime", "AirtimeTransfer")
    AirtimeTransfer.objects.exclude(recipient=None).exclude(recipient="").exclude(recipient__startswith="tel:").update(
        recipient=Concat(Value("tel:"), F("recipient"))
    )


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("airtime", "0012_auto_20191015_1704")]

    operations = [migrations.RunPython(recipients_to_urns, reverse)]