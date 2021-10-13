from django.db import models
# from django.contrib.auth.models import User
from users.models import UserProfile
from kubeadmin.models import KubePermission
from django.utils import timezone


class Projectlist(models.Model):
    type_choices = (
        ("deployment", '部署集'),
        ("statefulset", '有状态副本集')
    )
    status_choice = (
        ("create", "已申请"),
        ("approved", "已批准"),
        ("deny", "驳回"),
        ("PEDDING","执行中"),
        ("failed", "执行失败"),
        ("success", "执行成功")
    )
    project_name = models.CharField(max_length=255, verbose_name="项目名称",unique=True)
    project_namespace = models.CharField(max_length=255, verbose_name="项目组")
    project_image = models.CharField(max_length=255, verbose_name="项目立项镜像",unique=True)
    deploy_type = models.CharField(max_length=64,verbose_name='项目立项类别', choices=type_choices,
                                   help_text="deployment(无状态应用),statefulset(有状态应用)")
    project_replicas = models.CharField(max_length=64,verbose_name='副本数')
    project_port = models.CharField(max_length=64,verbose_name='应用端口')
    imagepullsecrets = models.CharField(max_length=255,verbose_name="使用的imagepullsecrets")
    project_createtime = models.DateTimeField(verbose_name='项目创建时间',default=timezone.now)
    project_status = models.CharField(max_length=255,verbose_name='项目状态',choices=status_choice,default='create')
    project_user = models.CharField(max_length=255, verbose_name="项目创建人")
    project_create_id = models.CharField(max_length=255, verbose_name="项目创建任务id", default='xx')
    project_volumecreate_id = models.CharField(max_length=255, verbose_name="项目存储创建任务id", default='xx')
    project_svc_id = models.CharField(max_length=255, verbose_name="项目服务网关创建任务id", default='xx')


    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = "立项列表"
        verbose_name_plural = verbose_name


class HostPassTable(models.Model):
    host_user = models.CharField(max_length=10,verbose_name='主机用户', unique=True)
    host_pass = models.CharField(max_length=255,verbose_name='主机密码')
    host_room = models.CharField(max_length=20,verbose_name='所在机房',unique=True)

    def __str__(self):
        return self.host_pass

    class Meta:
        verbose_name = "主机密码表"
        verbose_name_plural = verbose_name
