from django.views import View
from utils.kube import KubernetesAPI
from django.http import JsonResponse
from kubeadmin.models import KubeEnv
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from kubeadmin.models import KubePermission
from users.models import UserProfile
import pytz

import re
# Create your views here.


class KubesvcView(View):

    permission_classes = (IsAuthenticated,)

    def get(self,request):
        token = request.META.get ('HTTP_AUTHORIZATION', " ").split (' ')[1]
        data = {'token': token}
        try:
            valid_data = VerifyJSONWebTokenSerializer ().validate (data)
            user = valid_data['user']
            username = user
        except Exception as e:
            print("validation error", str(e))
        user_id = UserProfile.objects.filter (username=username).first().id
        svc_label = request.GET.get('svc_label')
        svc_nspace = request.GET.get('svc_nspace')
        svc_cluster = request.GET.get('svc_cluster')
        page = request.GET.get('page')
        limit = request.GET.get('limit')
        if svc_cluster:
            api_address = KubeEnv.objects.filter(k8s_ident=svc_cluster).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=svc_cluster).values('k8sapi_token')[0]['k8sapi_token']
        else:
            return JsonResponse ({'status': 403, 'message': "该用户集群权限"})
        kube_client = KubernetesAPI(api_host=api_address,token=api_token)
        if UserProfile.objects.filter(username=username).first().is_superuser:
            namespaces_set = kube_client.client_core_v1.list_namespace().items
        else:
            try:
                namespaces_set = KubePermission.objects.filter(user_name=username).values('kube_namespace')
            except Exception as e:
                return JsonResponse({'status': 403, 'message': "该用户没有命名空间权限",'total': 0})
        if not svc_nspace:
            if UserProfile.objects.filter(username=username).first().is_superuser:
                svc_nspace = 'default'
            else:
                try:
                    svc_nspace = KubePermission.objects.filter(user_name=username).first().kube_namespace
                except Exception as e:
                    return JsonResponse({'status': 403, 'message': "没有任何权限访问该集群，请联系管理员配置权限.",'total': 0})

        query_dict = {}
        for ns_item in namespaces_set:
            if UserProfile.objects.filter(username=username).first().is_superuser:
                namespace = ns_item.metadata.name
            else:
                namespace = ns_item['kube_namespace']
            query_dict[namespace] = []
            svc_set = kube_client.CoreV1Api.list_namespaced_service(namespace=namespace).items
            for items in svc_set:
                try:
                    if items.metadata.labels:
                        query_dict[namespace].append(items.metadata.labels['k8s-app'])
                except KeyError:
                    pass
            query_dict[namespace] = list(set(query_dict[namespace]))
        if svc_label:
            svc_set = kube_client.CoreV1Api.list_namespaced_service(namespace=svc_nspace,
                                                                    label_selector="k8s-app=%s" % svc_label).items
        else:
            svc_set = kube_client.CoreV1Api.list_namespaced_service(namespace=svc_nspace).items

        svc_list = []
        for items in svc_set:
            items_dict = dict()
            items_dict['svc_name'] = items.metadata.name
            items_dict['svc_namespace'] = items.metadata.namespace
            items_dict['svc_ip'] = items.spec.cluster_ip
            items_dict['create_time'] = str(items.metadata.creation_timestamp.astimezone(pytz.timezone('Asia/Shanghai')))
            items_dict['labels'] = str(items.spec.selector)
            items_dict['svc_type'] = items.spec.type
            items_dict['portlist'] = ",".join(str(port) for port in [str(i.port) + ":" + str(i.target_port) for i in items.spec.ports])
            svc_list.append(items_dict)
        all_numbers = len(svc_list)
        if all_numbers != 0:
            paginator = Paginator(svc_list,limit)
            contacts = paginator.page(page)
            list123 = contacts.object_list
        else:
            list123 = []
        return JsonResponse({'status': 200, 'message': "查询成功.", 'items': list123, 'total': all_numbers,
                             'query_dict': query_dict,'selected_ns':svc_nspace})

