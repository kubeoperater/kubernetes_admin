# Generated by Django 2.1.4 on 2019-12-19 15:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kubeitems', '0016_auto_20191218_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectlist',
            name='project_createtime',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 19, 15, 34, 9, 623786), verbose_name='项目创建时间'),
        ),
        migrations.AlterField(
            model_name='projectlist',
            name='project_status',
            field=models.CharField(choices=[('create', '已申请'), ('approved', '已批准'), ('deny', '驳回'), ('PEDDING', '执行中'), ('failed', '执行失败'), ('success', '执行成功')], default='create', max_length=255, verbose_name='项目状态'),
        ),
    ]
