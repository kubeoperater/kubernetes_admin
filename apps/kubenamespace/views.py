from utils.kube import KubernetesAPI
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from kubeadmin.models import KubeEnv,KubePermission
# Create your views here.


class GetNamespaceView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        k8s_ident = request.GET.get('cluster')
        nameonly = request.GET.get('nameonly')
        if k8s_ident:
            if request.user.is_superuser:
                try:
                    kube_host = KubeEnv.objects.get(k8s_ident=k8s_ident).k8sapi
                    kube_token = KubeEnv.objects.get(k8s_ident=k8s_ident).k8sapi_token
                    kube_client = KubernetesAPI(api_host=kube_host,token=kube_token)
                    namespace_result = kube_client.client_core_v1.list_namespace(timeout_seconds=10).items
                    namespace_list = []
                    if nameonly:
                        for item in namespace_result:
                            namespace_list.append(item.metadata.name)
                    else:
                        for item in namespace_result:
                            namespace_list.append(item.to_dict())

                    message = {'status': 200, 'data': namespace_list}

                except KeyError as e:
                    message = {'status': 500, 'message': str(e)}
            else:
                namespace_list = list(KubePermission.objects.filter(user_name=request.user.id).values('kube_namespace'))
                message = {'status': 200, 'data': namespace_list}
        else:
            message = {'status': 500, 'message': 'cluster params not found.'}

        return JsonResponse(message)
