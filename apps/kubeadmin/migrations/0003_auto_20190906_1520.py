# Generated by Django 2.1.4 on 2019-09-06 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kubeadmin', '0002_kubeenv_k8s_ident'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kubeenv',
            name='k8s_ident',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
