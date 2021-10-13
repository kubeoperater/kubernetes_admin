from django.db import models

# Create your models here.


class NodeLabels(models.Model):
    groupname = models.CharField(max_length=64, verbose_name=u"组名称", unique=True)
    groupident = models.CharField(max_length=64, verbose_name=u"组标识", unique=True)

    def __str__(self):
        return self.groupident

    class Meta:
        verbose_name = "组标识"
        verbose_name_plural = verbose_name
