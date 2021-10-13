from django.conf.urls import url
from django.urls import path
from .views import KubepodView, terminal_start, ContainerlogView, KubecontainlistView,KubepodlistView

urlpatterns = [
    path('getinfo/', KubepodView.as_view(), name="kubepod"),
    path('byns/', KubepodlistView.as_view (), name='kubepodlist'),
    path('containerbypod/', KubecontainlistView.as_view (), name='kubecontainerlist'),
    path('ssh/<str:k8s_apiport>/<str:namespace>/<str:pod_name>/<str:container_name>/<str:usertoken>/',terminal_start),
    path('log/', ContainerlogView.as_view(), name='kubelog')
]
