from django.db import models
# from django.contrib.auth.models import User
from users.models import UserProfile

# Create your models here.


class KubeEnv(models.Model):
    k8sapi = models.CharField(max_length=64, verbose_name=u"k8s连接地址",
                              unique=True,
                              help_text="例如 https://10.255.56.250:6444")
    k8sapi_token = models.TextField(verbose_name=u'k8s连接token',
                                    help_text="参考 apiserver token")
    k8s_name = models.CharField(max_length=255,
                                verbose_name='k8s集群名称',
                                default='default',unique=True,help_text="k8s集群名称")
    k8s_ident = models.CharField(max_length=255,unique=True,null=False)

    def __str__(self):
        return self.k8s_ident

    class Meta:
        verbose_name = "k8s集群"
        verbose_name_plural = verbose_name


class KubePermission(models.Model):
    user_name = models.ForeignKey(UserProfile, to_field='username',on_delete=models.CASCADE, verbose_name='用户名')
    k8sapi = models.ForeignKey(KubeEnv, to_field='k8s_ident',verbose_name='k8s集群', on_delete=models.CASCADE)
    kube_namespace = models.CharField(max_length=255, verbose_name='k8s命名空间',
                                 help_text='赋予用户某个命名空间的权限')
    kube_permis = models.CharField(max_length=100, verbose_name='命名空间权限',
                                   choices=(('read','read'),('manage','manage')),
                                   help_text='读写权限')

    def __str__(self):
        return "用户" + self.user_name.username + "访问集群" + self.k8sapi.k8s_name + "的" + self.kube_namespace + "空间" + \
               self.kube_permis + "权限"

    class Meta:
        verbose_name = "k8s权限"
        verbose_name_plural = verbose_name
        unique_together = (("user_name", "k8sapi", "kube_namespace"),)
