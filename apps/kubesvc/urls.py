from django.conf.urls import url
from .views import KubesvcView

urlpatterns = [
    url(r'^getinfo/', KubesvcView.as_view(), name="kubesvc"),
]
