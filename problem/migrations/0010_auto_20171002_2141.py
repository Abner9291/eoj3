# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-02 21:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0009_auto_20171001_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True)),
                ('parent_id', models.IntegerField(default=-1)),
                ('problem_list', models.TextField(blank=True)),
                ('priority', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='problem',
            name='checker',
            field=models.CharField(blank=True, max_length=64, verbose_name='Checker'),
        ),
    ]