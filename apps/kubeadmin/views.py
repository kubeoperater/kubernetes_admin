from .models import KubeEnv
from django.http import JsonResponse
import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class KubenvView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request):
        search_keywords = request.GET.get('pod_cluster')
        if search_keywords:
            env_list = list(KubeEnv.objects.filter(k8s_ident=search_keywords).values())
        else:
            env_list = list(KubeEnv.objects.all().values())
        return JsonResponse({'status': 200, 'message': "查询成功.", 'items': env_list,'total': len(env_list)})


class KubenvChangeView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self,request):

        if request.META.get('CONTENT_TYPE', '') == 'application/x-www-form-urlencoded':
            request_body = request.POST
        else:
            request_body = json.loads(request.body)
        if "action" in request_body:
            model_action = request_body['action']
            if model_action == "delete":
                env_id = request_body['id']
                KubeEnv.objects.filter(id=env_id).delete()
                return JsonResponse({'status': 200, 'message': "删除成功."})
            elif model_action == 'create':
                env_name = request_body['k8s_name']
                env_api = request_body['k8sapi']
                env_token = request_body['k8sapi_token']
                env_ident = request_body['k8s_ident']
                try:
                    create_obj = KubeEnv.objects.create(k8s_name=env_name, k8sapi=env_api,k8sapi_token=env_token,
                                                        k8s_ident=env_ident)
                    return JsonResponse({'status': 200, 'message': "创建成功.",'id': create_obj.id})
                except Exception as e:
                    return JsonResponse({'status': 500, 'message': str(e)})
            elif model_action == 'update':
                env_id = request_body['id']
                env_name = request_body['k8s_name']
                env_api = request_body['k8sapi']
                env_token = request_body['k8sapi_token']
                try:
                    KubeEnv.objects.filter(id=env_id).update(k8s_name=env_name, k8sapi=env_api, k8sapi_token=env_token)
                    return JsonResponse({'status': 200, 'message': "更新成功."})
                except Exception as e:
                    return JsonResponse({'status': 500, 'message': str(e)})
        else:
            return JsonResponse({'status': 500, 'message': '没有action参数，拒绝执行'})

