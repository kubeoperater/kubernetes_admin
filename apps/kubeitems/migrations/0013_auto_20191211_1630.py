# Generated by Django 2.1.4 on 2019-12-11 16:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kubeitems', '0012_auto_20191211_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectlist',
            name='project_createtime',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 11, 16, 30, 53, 646691), verbose_name='项目创建时间'),
        ),
    ]
