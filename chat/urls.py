from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from chat.views import user
router = DefaultRouter()
from django.conf import settings
from django.views import static

from . import views

router.register(r'userinfo', user.MyUserViewSet, basename='userinfo')

urlpatterns = [
    # path('', views.index, name='index'),
    re_path('media/(?P<path>.*)$', static.serve, {"document_root": settings.MEDIA_ROOT, }),
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += router.urls