# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-06 07:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdf',
            name='book',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='management.Book'),
        ),
    ]
