from django.conf.urls import url
from .views import UserinfoView,UserlistView,KubensPermise,UserlogoutView
urlpatterns = [
    url(r'^userinfo/', UserinfoView.as_view(), name="userinfo"),
    url(r'^userlist/', UserlistView.as_view(), name="userlist"),
    url(r'^userpermission/', KubensPermise.as_view(), name="userpermission"),
    url (r'^logout/', UserlogoutView.as_view (), name="userlogout"),
]
