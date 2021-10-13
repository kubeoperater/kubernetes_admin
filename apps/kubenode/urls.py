from django.conf.urls import url

from .views import KubenodeView

urlpatterns = [
    url(r'^getinfo/', KubenodeView.as_view(), name="getinfo"),
]

