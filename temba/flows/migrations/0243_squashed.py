# Generated by Django 2.2.10 on 2020-12-04 17:21

import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import temba.utils.json
import temba.utils.models
import temba.utils.uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contacts", "0128_squashed"),
        ("campaigns", "0036_squashed"),
        ("channels", "0124_squashed"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExportFlowResultsTask",
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
                (
                    "uuid",
                    models.CharField(
                        db_index=True,
                        default=temba.utils.models.generate_uuid,
                        help_text="The unique identifier for this object",
                        max_length=36,
                        unique=True,
                        verbose_name="Unique Identifier",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("P", "Pending"), ("O", "Processing"), ("C", "Complete"), ("F", "Failed")],
                        default="P",
                        max_length=1,
                    ),
                ),
                (
                    "config",
                    temba.utils.models.JSONAsTextField(
                        default=dict, help_text="Any configuration options for this flow export", null=True
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Flow",
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
                (
                    "uuid",
                    models.CharField(
                        db_index=True,
                        default=temba.utils.models.generate_uuid,
                        help_text="The unique identifier for this object",
                        max_length=36,
                        unique=True,
                        verbose_name="Unique Identifier",
                    ),
                ),
                ("name", models.CharField(help_text="The name for this flow", max_length=64)),
                ("is_archived", models.BooleanField(default=False, help_text="Whether this flow is archived")),
                ("is_system", models.BooleanField(default=False, help_text="Whether this is a system created flow")),
                (
                    "flow_type",
                    models.CharField(
                        choices=[
                            ("M", "Message flow"),
                            ("V", "Phone call flow"),
                            ("S", "Surveyor flow"),
                            ("U", "USSD flow"),
                        ],
                        default="M",
                        help_text="The type of this flow",
                        max_length=1,
                    ),
                ),
                ("metadata", temba.utils.models.JSONAsTextField(default=dict, null=True)),
                (
                    "expires_after_minutes",
                    models.IntegerField(
                        default=10080, help_text="Minutes of inactivity that will cause expiration from flow"
                    ),
                ),
                (
                    "ignore_triggers",
                    models.BooleanField(default=False, help_text="Ignore keyword triggers while in this flow"),
                ),
                ("saved_on", models.DateTimeField(auto_now_add=True, help_text="When this item was saved")),
                (
                    "base_language",
                    models.CharField(
                        blank=True,
                        default="base",
                        help_text="The authoring language, additional languages can be added later",
                        max_length=4,
                        null=True,
                    ),
                ),
                (
                    "version_number",
                    models.CharField(
                        default="11.12", help_text="The flow version this definition is in", max_length=8
                    ),
                ),
            ],
            options={"ordering": ("-modified_on",)},
        ),
        migrations.CreateModel(
            name="FlowCategoryCount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "is_squashed",
                    models.BooleanField(default=False, help_text="Whether this row was created by squashing"),
                ),
                ("node_uuid", models.UUIDField(db_index=True)),
                ("result_key", models.CharField(max_length=128)),
                ("result_name", models.CharField(max_length=128)),
                ("category_name", models.CharField(max_length=128)),
                ("count", models.IntegerField(default=0)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="FlowLabel",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "uuid",
                    models.CharField(
                        db_index=True, default=temba.utils.models.generate_uuid, max_length=36, unique=True
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="The name of this flow label", max_length=64, verbose_name="Name"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FlowNodeCount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "is_squashed",
                    models.BooleanField(default=False, help_text="Whether this row was created by squashing"),
                ),
                ("node_uuid", models.UUIDField(db_index=True)),
                ("count", models.IntegerField(default=0)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="FlowPathCount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "is_squashed",
                    models.BooleanField(default=False, help_text="Whether this row was created by squashing"),
                ),
                ("from_uuid", models.UUIDField()),
                ("to_uuid", models.UUIDField()),
                ("period", models.DateTimeField()),
                ("count", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="FlowPathRecentRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("from_uuid", models.UUIDField()),
                ("from_step_uuid", models.UUIDField()),
                ("to_uuid", models.UUIDField()),
                ("to_step_uuid", models.UUIDField()),
                ("visited_on", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="FlowRevision",
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
                ("definition", temba.utils.models.JSONAsTextField(default=dict, help_text="The JSON flow definition")),
                (
                    "spec_version",
                    models.CharField(
                        default="11.12", help_text="The flow version this definition is in", max_length=8
                    ),
                ),
                ("revision", models.IntegerField(help_text="Revision number for this definition", null=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="FlowRun",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=temba.utils.uuid.uuid4, unique=True)),
                (
                    "status",
                    models.CharField(
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
                ("created_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("exited_on", models.DateTimeField(null=True)),
                ("expires_on", models.DateTimeField(null=True)),
                ("responded", models.BooleanField(default=False)),
                ("parent_uuid", models.UUIDField(null=True)),
                ("results", temba.utils.models.JSONAsTextField(default=dict, null=True)),
                ("path", temba.utils.models.JSONAsTextField(default=list, null=True)),
                ("events", temba.utils.models.JSONField(encoder=temba.utils.json.TembaEncoder, null=True)),
                ("current_node_uuid", models.UUIDField(null=True)),
                (
                    "delete_reason",
                    models.CharField(choices=[("A", "Archive delete"), ("U", "User delete")], max_length=1, null=True),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "exit_type",
                    models.CharField(
                        choices=[("C", "Completed"), ("I", "Interrupted"), ("E", "Expired")], max_length=1, null=True
                    ),
                ),
            ],
            bases=(temba.utils.models.RequireUpdateFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name="FlowRunCount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "is_squashed",
                    models.BooleanField(default=False, help_text="Whether this row was created by squashing"),
                ),
                (
                    "exit_type",
                    models.CharField(
                        choices=[("C", "Completed"), ("I", "Interrupted"), ("E", "Expired")], max_length=1, null=True
                    ),
                ),
                ("count", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="FlowSession",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(unique=True)),
                (
                    "session_type",
                    models.CharField(
                        choices=[
                            ("M", "Message flow"),
                            ("V", "Phone call flow"),
                            ("S", "Surveyor flow"),
                            ("U", "USSD flow"),
                        ],
                        default="M",
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("W", "Waiting"),
                            ("C", "Completed"),
                            ("I", "Interrupted"),
                            ("X", "Expired"),
                            ("F", "Failed"),
                        ],
                        max_length=1,
                        null=True,
                    ),
                ),
                ("responded", models.BooleanField(default=False)),
                ("output", temba.utils.models.JSONAsTextField(default=dict, null=True)),
                ("created_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("ended_on", models.DateTimeField(null=True)),
                ("timeout_on", models.DateTimeField(null=True)),
                ("wait_started_on", models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="FlowStart",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=temba.utils.uuid.uuid4, unique=True)),
                (
                    "start_type",
                    models.CharField(
                        choices=[
                            ("M", "Manual"),
                            ("A", "API"),
                            ("Z", "Zapier"),
                            ("F", "Flow Action"),
                            ("T", "Trigger"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "urns",
                    django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None),
                ),
                ("query", models.TextField(null=True)),
                ("restart_participants", models.BooleanField(default=True)),
                ("include_active", models.BooleanField(default=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("P", "Pending"), ("S", "Starting"), ("C", "Complete"), ("F", "Failed")],
                        default="P",
                        max_length=1,
                    ),
                ),
                ("extra", temba.utils.models.JSONAsTextField(default=dict, null=True)),
                ("parent_summary", temba.utils.models.JSONField(encoder=temba.utils.json.TembaEncoder, null=True)),
                ("session_history", temba.utils.models.JSONField(encoder=temba.utils.json.TembaEncoder, null=True)),
                ("created_on", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("modified_on", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("contact_count", models.IntegerField(default=0, null=True)),
                (
                    "campaign_event",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="flow_starts",
                        to="campaigns.CampaignEvent",
                    ),
                ),
                ("connections", models.ManyToManyField(related_name="starts", to="channels.ChannelConnection")),
                ("contacts", models.ManyToManyField(to="contacts.Contact")),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="flow_starts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "flow",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="starts", to="flows.Flow"
                    ),
                ),
                ("groups", models.ManyToManyField(to="contacts.ContactGroup")),
            ],
        ),
        migrations.CreateModel(
            name="FlowStartCount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "is_squashed",
                    models.BooleanField(default=False, help_text="Whether this row was created by squashing"),
                ),
                ("count", models.IntegerField(default=0)),
                (
                    "start",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="counts", to="flows.FlowStart"
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]