# Generated by Django 2.1.4 on 2019-12-03 14:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kubeitems', '0003_auto_20191203_1312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectlist',
            name='env_set',
        ),
        migrations.AddField(
            model_name='projectlist',
            name='project_createtime',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 3, 14, 20, 0, 341087), verbose_name='项目创建时间'),
        ),
    ]
