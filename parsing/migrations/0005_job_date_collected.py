# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-23 00:48
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsing', '0004_job_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='date_collected',
            field=models.DateField(default=datetime.date(2016, 3, 23)),
            preserve_default=False,
        ),
    ]
