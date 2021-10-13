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


class KubedepView(APIView):

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
        dep_label = request.GET.get('dep_label')
        dep_cluster = request.GET.get('dep_cluster')
        dep_nspace = request.GET.get('dep_nspace')
        page = request.GET.get('page')
        limit = request.GET.get('limit')
        if dep_cluster:
            api_address = KubeEnv.objects.filter(k8s_ident=dep_cluster).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=dep_cluster).values('k8sapi_token')[0]['k8sapi_token']
        else:
            return JsonResponse({'status': 403, 'message': "该用户集群权限"})
        try:
            kube_client = KubernetesAPI(api_host=api_address, token=api_token)
        except Exception as e:
            print(str(e))
        if UserProfile.objects.filter(username=username).first().is_superuser:
            namespaces_set = kube_client.client_core_v1.list_namespace().items
        else:
            try:
                namespaces_set = KubePermission.objects.filter(user_name=username).values('kube_namespace')
            except Exception as e:
                return JsonResponse(dict (status=403, message="该用户没有命名空间权限"))
        if not dep_nspace:
            if UserProfile.objects.filter(username=username).first().is_superuser:
                dep_nspace = 'default'
            else:
                try:
                    dep_nspace = KubePermission.objects.filter(user_name=username).first().kube_namespace
                except Exception as e:
                    return JsonResponse(dict(status=403, message="没有任何权限访问该集群，请联系管理员配置权限.", total=0))
        query_dict = {}
        for ns_item in namespaces_set:
            if UserProfile.objects.filter(username=username).first().is_superuser:
                namespace = ns_item.metadata.name
            else:
                namespace = ns_item['kube_namespace']
            query_dict[namespace] = []
            dep_set = kube_client.client_apps_v1.list_namespaced_deployment(namespace=namespace).items
            for items in dep_set:
                try:
                    query_dict[namespace].append(items.metadata.labels['k8s-app'])
                except KeyError:
                    pass
            query_dict[namespace] = list(set(query_dict[namespace]))
        if dep_label:
            dep_set = kube_client.client_apps_v1.list_namespaced_deployment(namespace=dep_nspace,
                                                                            label_selector="k8s-app=%s" % dep_label).items
        else:
            dep_set = kube_client.client_apps_v1.list_namespaced_deployment(namespace=dep_nspace).items
        label_list = []
        for nodeinfo in kube_client.client_core_v1.list_node().items:
            if 'appgroup' in nodeinfo.metadata.labels:
                label_list.append(nodeinfo.metadata.labels['appgroup'])
        label_list2 = list(set(label_list))
        dep_list = []
        for items in dep_set:
            items_dict = dict()
            items_dict['dep_name'] = items.metadata.name
            items_dict['dep_namespace'] = items.metadata.namespace
            items_dict['dep_creatime'] = str(items.metadata.creation_timestamp.astimezone(pytz.timezone('Asia/Shanghai')))
            items_dict['dep_labels'] = items.metadata.labels
            items_dict['dep_selectlabels'] = items.spec.selector.match_labels
            items_dict['dep_replicas'] = items.spec.replicas
            items_dict['dep_available_replicas'] = items.status.available_replicas
            items_dict['img_list'] = ','.join([container.image for container in items.spec.template.spec.containers])
            items_dict['container_list'] = ','.join([container.name for container in items.spec.template.spec.containers])
            items_dict['label_list'] = ','.join(label_list2)
            dep_list.append(items_dict)
        all_numbers = len(dep_list)
        if all_numbers != 0:
            paginator = Paginator(dep_list,limit)
            contacts = paginator.page(page)
            list123 = contacts.object_list
        else:
            list123 = []
        return JsonResponse(dict(status=200, message="查询成功.", items=list123, total=all_numbers, query_dict=query_dict,
                                  selected_ns=dep_nspace))


class KubedepChangeView(APIView):

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
            dep_name = request_body['dep_name']
            dep_namespace = request_body['dep_namespace']
            if model_action == "delete":
                try:
                    delete_status = kube_client.client_apps_v1.delete_namespaced_deployment(name=dep_name, namespace=dep_namespace)
                    return JsonResponse(dict(status=200, message=delete_status.status))
                except Exception as e:
                    return JsonResponse(dict(status=e.status, message=e.reason))

            elif model_action == 'update':
                scale_num = request_body['dep_replicas']
                patch_body = {"spec": {"replicas": int(scale_num)}}
                if "dep_containame" in request_body and "contain_image" in request_body:
                    contain_name = str(request_body['dep_containame']).strip()
                    contain_image = str(request_body['contain_image']).strip()
                    patch_body['spec']['template'] = {"spec": {"containers":[{"name": contain_name, "image": contain_image}]}}
                elif "dep_nodename" in request_body:
                    dep_nodename = request_body['dep_nodename']
                    patch_body['spec']['template'] = {"spec": {"nodeSelector":{"appgroup": dep_nodename}}}

                try:
                    update_status = kube_client.client_apps_v1.patch_namespaced_deployment(name=dep_name,
                                    namespace=dep_namespace, body=patch_body)
                    return JsonResponse(dict(status=200, message=str(patch_body)))
                except Exception as e:
                    return JsonResponse(dict(status=500, message=str(e)))
        else:
            pass
