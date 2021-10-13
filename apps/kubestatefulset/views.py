from rest_framework.views import APIView
from utils.kube import KubernetesAPI
from django.http import JsonResponse
from kubeadmin.models import KubeEnv
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile
from kubeadmin.models import KubePermission
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
import pytz
import json
# Create your views here.


class kubestatefulsetView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        data = {'token': token}
        try:
            valid_data = VerifyJSONWebTokenSerializer().validate(data)
            user = valid_data['user']
            username = user
        except Exception as e:
            return JsonResponse({"validation error", e})
        statefulset_label = request.GET.get('statefulset_label')
        statefulset_cluster = request.GET.get('statefulset_cluster')
        statefulset_nspace = request.GET.get('statefulset_nspace')
        page = request.GET.get('page')
        limit = request.GET.get('limit')
        if statefulset_cluster:
            api_address = KubeEnv.objects.filter(k8s_ident=statefulset_cluster).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=statefulset_cluster).values('k8sapi_token')[0]['k8sapi_token']
        else:
            return JsonResponse({'status': 403, 'message': "该用户集群权限"})
        kube_client = KubernetesAPI(api_host=api_address, token=api_token)
        if UserProfile.objects.filter(username=username).first().is_superuser:
            namespaces_set = kube_client.client_core_v1.list_namespace().items
        else:
            try:
                namespaces_set = KubePermission.objects.filter(user_name=username).values('kube_namespace')
            except Exception as e:
                return JsonResponse({'status': 403, 'message': "该用户没有命名空间权限"})
        if not statefulset_nspace:
            if UserProfile.objects.filter(username=username).first().is_superuser:
                statefulset_nspace = 'default'
            else:
                try:
                    statefulset_nspace = KubePermission.objects.filter(user_name=username).first().kube_namespace
                except Exception as e:
                    return JsonResponse({'status': 403, 'message': "没有任何权限访问该集群，请联系管理员配置权限.",'total': 0})
        query_dict = {}
        for ns_item in namespaces_set:
            if UserProfile.objects.filter(username=username).first().is_superuser:
                namespace = ns_item.metadata.name
            else:
                namespace = ns_item['kube_namespace']
            query_dict[namespace] = []
            statefulset_set = kube_client.client_apps_v1.list_namespaced_stateful_set(namespace=namespace).items
            for items in statefulset_set:
                try:
                    query_dict[namespace].append(items.spec.selector.match_labels['k8s-app'])
                except KeyError:
                    pass
            query_dict[namespace] = list(set(query_dict[namespace]))
        if statefulset_label:
            statefulset_set = kube_client.client_apps_v1.list_namespaced_stateful_set(namespace=statefulset_nspace,
                                                                            label_selector="k8s-app=%s" % statefulset_label).items
        else:
            statefulset_set = kube_client.client_apps_v1.list_namespaced_stateful_set(namespace=statefulset_nspace).items
        label_list = []
        for nodeinfo in kube_client.client_core_v1.list_node().items:
            if 'appgroup' in nodeinfo.metadata.labels:
                label_list.append(nodeinfo.metadata.labels['appgroup'])
        label_list2 = list(set(label_list))
        print(label_list2)
        statefulset_list = []
        for items in statefulset_set:
            items_dict = dict()
            items_dict['statefulset_name'] = items.metadata.name
            items_dict['statefulset_namespace'] = items.metadata.namespace
            items_dict['statefulset_creatime'] = str(items.metadata.creation_timestamp.astimezone(pytz.timezone('Asia/Shanghai')))
            items_dict['statefulset_labels'] = items.metadata.labels
            items_dict['statefulset_selectlabels'] = items.spec.selector.match_labels
            items_dict['statefulset_replicas'] = items.spec.replicas
            items_dict['statefulset_available_replicas'] = items.status.ready_replicas
            items_dict['img_list'] = ','.join([container.image for container in items.spec.template.spec.containers])
            items_dict['container_list'] = ','.join([container.name for container in items.spec.template.spec.containers])
            items_dict['label_list'] = ','.join(label_list2)
            statefulset_list.append(items_dict)
        all_numbers = len(statefulset_list)
        if all_numbers != 0:
            paginator = Paginator(statefulset_list,limit)
            contacts = paginator.page(page)
            list123 = contacts.object_list
        else:
            list123 = []
        return JsonResponse({'status': 200, 'message': "查询成功.", 'items': list123, 'total': all_numbers,
                             'query_dict': query_dict,'selected_ns':statefulset_nspace})


class kubestatefulsetChangeView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self,request):
        if request.META.get('CONTENT_TYPE', '') == 'application/x-www-form-urlencoded':
            request_body = request.POST
        else:
            request_body = json.loads(request.body)

        cluster_alias = request_body['cluster']
        api_address = KubeEnv.objects.filter(k8s_ident=cluster_alias).values('k8sapi')[0]['k8sapi']
        api_token = KubeEnv.objects.filter(k8s_ident=cluster_alias).values('k8sapi_token')[0]['k8sapi_token']
        kube_client = KubernetesAPI(api_host=api_address, token=api_token)
        if "action" in request_body:
            model_action = request_body['action']
            statefulset_name = request_body['statefulset_name']
            statefulset_namespace = request_body['statefulset_namespace']
            if model_action == "delete":
                try:
                    delete_status = kube_client.client_apps_v1.delete_namespaced_stateful_set(name=statefulset_name,namespace=statefulset_namespace)
                    return JsonResponse({'status': 200, 'message': delete_status.status})
                except Exception as e:
                    return JsonResponse({'status': 500, 'message': e})

            elif model_action == 'update':
                scale_num = request_body['statefulset_replicas']
                patch_body = {"spec": {"replicas": int (scale_num)}}
                if "contain_name" in request_body and "contain_image" in request_body :
                    contain_name = str(request_body['contain_name']).strip()
                    contain_image = str(request_body['contain_image']).strip()
                    patch_body['spec']['template'] = { "spec": {"containers":[ { "name": contain_name, "image": contain_image}]}}
                elif "statefulset_nodename" in request_body:
                    statefulset_nodename = request_body['statefulset_nodename']
                    patch_body['spec']['template'] = {"spec": {"nodeSelector":{"appgroup": statefulset_nodename}}}

                try:
                    update_status = kube_client.client_apps_v1.patch_namespaced_stateful_set(name=statefulset_name,
                                                                                             namespace=statefulset_namespace,body=patch_body)
                    return JsonResponse({'status': 200, 'message': str(patch_body)})
                except Exception as e:
                    return JsonResponse({'status': 500, 'message': str(e) })
        else:
            pass
