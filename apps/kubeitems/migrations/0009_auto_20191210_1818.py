# Generated by Django 2.1.4 on 2019-12-10 18:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kubeitems', '0008_auto_20191203_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectlist',
            name='project_createtime',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 10, 18, 18, 47, 741044), verbose_name='项目创建时间'),
        ),
    ]