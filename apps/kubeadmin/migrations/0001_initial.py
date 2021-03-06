# Generated by Django 2.1.4 on 2019-09-06 12:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KubeEnv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('k8sapi', models.CharField(help_text='例如 https://10.255.56.250:6444', max_length=64, unique=True, verbose_name='k8s连接地址')),
                ('k8sapi_token', models.TextField(help_text='参考 apiserver token', verbose_name='k8s连接token')),
                ('k8s_name', models.CharField(default='default', help_text='k8s集群名称', max_length=255, unique=True, verbose_name='k8s集群名称')),
            ],
            options={
                'verbose_name': 'k8s集群',
                'verbose_name_plural': 'k8s集群',
            },
        ),
        migrations.CreateModel(
            name='KubePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kube_namespace', models.CharField(help_text='赋予用户某个命名空间的权限', max_length=255, verbose_name='k8s命名空间')),
                ('kube_permis', models.CharField(choices=[('read', 'read'), ('manage', 'manage')], help_text='读写权限', max_length=100, verbose_name='命名空间权限')),
                ('k8sapi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kubeadmin.KubeEnv', to_field='k8s_name', verbose_name='k8s集群')),
                ('user_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username', verbose_name='用户名')),
            ],
            options={
                'verbose_name': 'k8s权限',
                'verbose_name_plural': 'k8s权限',
            },
        ),
        migrations.AlterUniqueTogether(
            name='kubepermission',
            unique_together={('user_name', 'k8sapi', 'kube_namespace')},
        ),
    ]
