# Generated by Django 2.1.4 on 2019-12-18 13:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kubeitems', '0014_auto_20191218_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectlist',
            name='project_createtime',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 18, 13, 52, 2, 101914), verbose_name='项目创建时间'),
        ),
        migrations.AlterField(
            model_name='projectlist',
            name='project_status',
            field=models.CharField(choices=[('create', '已申请'), ('approved', '已批准'), ('deny', '驳回'), ('PEDDING', '执行中'), ('failed', '执行失败'), ('success', '执行成功')], max_length=255, verbose_name='项目状态'),
        ),
    ]
