# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-22 23:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20170508_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(blank=True, max_length=30, verbose_name='nickname'),
        ),
        migrations.AlterField(
            model_name='user',
            name='school',
            field=models.CharField(blank=True, max_length=64, verbose_name='school'),
        ),
    ]
