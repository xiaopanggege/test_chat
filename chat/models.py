from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
# Create your models here.


# 继承admin的user表，不在这方面花太多精力自己做用户管理
class MyUser(AbstractUser):
    # model存储图片到media的目录下，注意更新这个avatar的时候是不会自动删除media目录下旧的图片的，需要安装django-cleanup或者自己用
    # signal来实现
    avatar = models.ImageField(upload_to='avatar/%Y/%m', max_length=200, verbose_name='用户头像',
                               default='avatar/default.png')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.username