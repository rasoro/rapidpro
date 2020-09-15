# Generated by Django 2.2.10 on 2020-09-15 14:12

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import temba.contacts.models


class Migration(migrations.Migration):

    dependencies = [
        ("orgs", "0068_org_plan_end"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contacts", "0122_auto_20200826_1853"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactImport",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Whether this item is active, use this instead of deleting"
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="When this item was originally created",
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="When this item was last modified",
                    ),
                ),
                ("file", models.FileField(upload_to=temba.contacts.models.get_import_upload_path)),
                ("mappings", django.contrib.postgres.fields.jsonb.JSONField()),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="The user which originally created this item",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contacts_contactimport_creations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        help_text="The user which last modified this item",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contacts_contactimport_modifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "org",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="contact_imports", to="orgs.Org"
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ContactImportBatch",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[("P", "Pending"), ("O", "Processing"), ("C", "Complete"), ("F", "Failed")],
                        default="P",
                        max_length=1,
                    ),
                ),
                ("specs", models.TextField()),
                ("row_start", models.IntegerField()),
                ("row_end", models.IntegerField()),
                ("num_created", models.IntegerField(default=0)),
                ("num_updated", models.IntegerField(default=0)),
                ("errors", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                (
                    "contact_import",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="batches",
                        to="contacts.ContactImport",
                    ),
                ),
            ],
        ),
    ]