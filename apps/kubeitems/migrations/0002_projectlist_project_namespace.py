# Generated by Django 2.1.4 on 2019-12-03 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kubeitems', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectlist',
            name='project_namespace',
            field=models.CharField(default='abc', max_length=255, verbose_name='项目组'),
        ),
    ]
