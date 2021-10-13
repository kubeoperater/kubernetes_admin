from django.conf.urls import url
from .views import kubestatefulsetView,kubestatefulsetChangeView
urlpatterns = [
    url(r'^getinfo/', kubestatefulsetView.as_view(), name="kubestatefulset"),
    url(r'^change/',kubestatefulsetChangeView.as_view(),name="kubestatefulsetchange"),
]

