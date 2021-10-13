import xadmin

# Register your models here.

from .models import KubePermission,KubeEnv


class KubeEnvAdmin(object):
    list_display = ('k8s_name','k8sapi')
    list_filter = ('k8s_name','k8sapi')
    search_fields = ('k8s_name','k8sapi')
    model_icon = 'fa fa-adn'


class KubePermissionAdmin(object):
    list_display = ('user_name','k8sapi','kube_namespace','kube_permis')
    list_filter = ('user_name__username','k8sapi__k8sapi','kube_namespace','kube_permis')
    search_fields = ('user_name__username','k8sapi__k8sapi','kube_namespace','kube_permis')
    # model_icon = 'fa fa-adn'
    # add_form_template = 'add_permission.html'
    #
    # def get_media(self):
    #     # media is the parent's return value (modified by any plugins)
    #     media = super(KubePermissionAdmin, self).get_media()
    #     media += self.vendor('xadmin.custom.getnamespace.js', )
    #     return media

xadmin.site.register(KubePermission, KubePermissionAdmin)
xadmin.site.register(KubeEnv,KubeEnvAdmin)
