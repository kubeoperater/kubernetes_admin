from django.conf.urls import url
from .views import KubedepView,KubedepChangeView
urlpatterns = [
    url(r'^getinfo/', KubedepView.as_view(), name="kubedep"),
    url(r'^change/',KubedepChangeView.as_view(),name="kubedepchange")
]

