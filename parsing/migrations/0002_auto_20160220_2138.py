# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-20 21:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parsing', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='salray_waged',
            new_name='salary_waged',
        ),
    ]
