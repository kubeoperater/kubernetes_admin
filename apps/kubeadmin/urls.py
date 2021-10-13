from django.conf.urls import url, include
from .views import KubenvView,KubenvChangeView

urlpatterns = [
    url(r'^getinfo/', KubenvView.as_view(), name="kubenv"),
    url(r'^change/', KubenvChangeView.as_view(), name="change"),
]
