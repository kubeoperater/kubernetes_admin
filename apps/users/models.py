from django.db import models
from django.contrib.auth.models import AbstractUser
import django.utils.timezone as timezone
# Create your models here.


def one_day_hence():
    return timezone.now() + timezone.timedelta(days=1)


class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=50, verbose_name=u"昵称", default="")
    birthday = models.DateField(verbose_name=u"生日", null=True, blank=True)
    gender = models.CharField(max_length=6, choices=(("male",u"男"),("female","女")), default="male")
    address = models.CharField(max_length=100, default=u"")
    mobile = models.CharField(max_length=11, null=True, blank=True)
    image = models.ImageField(upload_to="image/%Y/%m",default=u"image/default.png", max_length=100)
    login_token = models.CharField (max_length=255, default="", verbose_name='用户当前token')
    token_expires = models.DateTimeField(default=one_day_hence,verbose_name='token有效期')

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
