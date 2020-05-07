# Generated by Django 2.2.4 on 2020-05-07 18:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0138_remove_broadcast_recipient_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='msg',
            name='next_attempt',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text='When we should next attempt to deliver this message', null=True, verbose_name='Next Attempt'),
        ),
        migrations.AddIndex(
            model_name='msg',
            index=models.Index(condition=models.Q(('direction', 'O'), ('next_attempt__isnull', False), ('status', 'E')), fields=['next_attempt', 'created_on'], name='msgs_msg_errored_retry'),
        ),
    ]
