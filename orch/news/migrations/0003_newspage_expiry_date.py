# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20161016_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='expiry_date',
            field=models.DateTimeField(null=True, help_text="Use this field to determine a date after which this news item should no longer be treated as 'current' (i.e. to retire from home page)."),
        ),
    ]
