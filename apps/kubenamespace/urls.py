from django.urls import path, re_path
from .views import GetNamespaceView

urlpatterns = [
    re_path(r'^getinfo/', GetNamespaceView.as_view(), name="getinfo"),
]

