# Generated by Django 2.1.4 on 2019-09-06 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kubeadmin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kubeenv',
            name='k8s_ident',
            field=models.CharField(default='noew', max_length=255, unique=True),
        ),
    ]
