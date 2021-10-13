from django.urls import path, re_path
from .views import ProjectchangeView,ProjectListView,ProjectDeployView,ProjectTaskView

urlpatterns = [
    re_path(r'^projectchange/', ProjectchangeView.as_view(), name="projectchange"),
    re_path(r'^projectlist/', ProjectListView.as_view(), name="projectlist"),
    re_path(r'^projectdeploy/',ProjectDeployView.as_view(),name='projectdeploy'),
    re_path(r'^projectaskinfo/',ProjectTaskView.as_view(),name='projectaskinfo')
]