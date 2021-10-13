from rest_framework.views import APIView
from utils.kube import K8SStreamThread, KubernetesAPI
from dwebsocket.decorators import require_websocket
from django.http import JsonResponse
from kubeadmin.models import KubeEnv
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile
from kubeadmin.models import KubePermission
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
import pytz
from datetime import datetime
import logging
from utils.kafka_handler import KafkaHandler
from django.conf import settings

# Create your views here.


class KubepodlistView(APIView):

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
        pod_cluster = request.GET.get('cluster')
        pod_nspace = request.GET.get('pod_nspace')
        if pod_cluster:
            api_address = KubeEnv.objects.filter(k8s_ident=pod_cluster).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=pod_cluster).values('k8sapi_token')[0]['k8sapi_token']
        else:
            return JsonResponse({'status': 403, 'message': "该用户没有集群权限"})
        kube_client = KubernetesAPI(api_host=api_address, token=api_token)
        podlist = []
        for podinfo in kube_client.client_core_v1.list_namespaced_pod(namespace=pod_nspace).items:
            try:
                podlist.append(podinfo.metadata.name)
            except KeyError as e:
                pass
        return JsonResponse({'status': 200, 'message': "查询成功", 'list': podlist})


class KubecontainlistView(APIView):

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
        pod_cluster = request.GET.get('cluster')
        pod_nspace = request.GET.get('pod_nspace')
        pod_name = request.GET.get('pod_name')
        if pod_cluster:
            api_address = KubeEnv.objects.filter(k8s_ident=pod_cluster).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=pod_cluster).values('k8sapi_token')[0]['k8sapi_token']
        else:
            return JsonResponse({'status': 403, 'message': "该用户集群权限"})

        kube_client = KubernetesAPI(api_host=api_address, token=api_token)
        try:
            containset = kube_client.client_core_v1.list_namespaced_pod(namespace=pod_nspace, field_selector="metadata.name=%s" %
                                                                                                         pod_name).items

            containlist = [container.name for container in containset[0].status.container_statuses]
        except KeyError as e:
            print(e)
            containlist = []
        return JsonResponse({'status': 200, 'message': "查询成功", 'list': containlist})


class KubepodView(APIView):

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
        pod_label = request.GET.get('pod_label')
        pod_cluster = request.GET.get('pod_cluster')
        pod_nspace = request.GET.get('pod_nspace')
        page = request.GET.get('page')
        limit = request.GET.get('limit')
        pod_stats = request.GET.get('pod_stats')
        if pod_cluster:
            api_address = KubeEnv.objects.filter(k8s_ident=pod_cluster).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=pod_cluster).values('k8sapi_token')[0]['k8sapi_token']
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
        if not pod_nspace:
            if UserProfile.objects.filter(username=username).first().is_superuser:
                pod_nspace = 'default'
            else:
                try:
                    pod_nspace = KubePermission.objects.filter(user_name=username).first().kube_namespace
                except Exception as e:
                    return JsonResponse({'status': 403, 'message': "没有任何权限访问该集群，请联系管理员配置权限.",'total': 0})
        query_dict = {}
        for ns_item in namespaces_set:
            if UserProfile.objects.filter(username=username).first().is_superuser:
                namespace = ns_item.metadata.name
            else:
                namespace = ns_item['kube_namespace']
            query_dict[namespace] = []
            pod_set = kube_client.client_core_v1.list_namespaced_pod(namespace=namespace).items
            for items in pod_set:
                try:
                    query_dict[namespace].append(items.metadata.labels['k8s-app'])
                except KeyError:
                    pass
            query_dict[namespace] = list(set(query_dict[namespace]))
        if pod_label:
            pod_set = kube_client.client_core_v1.list_namespaced_pod(namespace=pod_nspace,
                                                                     label_selector="k8s-app=%s" % pod_label).items
        else:
            pod_set = kube_client.client_core_v1.list_namespaced_pod(namespace=pod_nspace).items

        pod_list = []
        for items in pod_set:
            items_dict = dict()
            if pod_stats:
                if pod_stats == 'Running' and items.status.phase == 'Running':
                    items_dict['pod_name'] = items.metadata.name
                    items_dict['pod_appname'] = items.metadata.labels['k8s-app']
                    items_dict['pod_namespace'] = items.metadata.namespace
                    items_dict['pod_creatime'] = str(items.metadata.creation_timestamp)
                    items_dict['host_ip'] = items.status.host_ip
                    items_dict['pod_ip'] = items.status.pod_ip
                    items_dict['img_rel'] = ",".join([x.image for x in items.spec.containers])
                    items_dict['pod_status'] = items.status.phase
                    items_dict['container_name_list'] = ','.join(
                        [container.name for container in items.status.container_statuses])
                    pod_list.append(items_dict)
                elif items.status.phase != 'Running' and pod_stats != 'Running':
                    items_dict['pod_name'] = items.metadata.name
                    items_dict['pod_appname'] = items.metadata.labels['k8s-app']
                    items_dict['pod_namespace'] = items.metadata.namespace
                    items_dict['pod_creatime'] = str(items.metadata.creation_timestamp.astimezone(pytz.timezone('Asia/Shanghai')))
                    print(items_dict['pod_creatime'])
                    items_dict['host_ip'] = items.status.host_ip
                    items_dict['pod_ip'] = items.status.pod_ip
                    items_dict['img_rel'] = ",".join([x.image for x in items.spec.containers])
                    items_dict['pod_status'] = items.status.phase
                    items_dict['container_name_list'] = ','.join(
                        [container.name for container in items.status.container_statuses])
                    pod_list.append(items_dict)

            else:
                items_dict['pod_name'] = items.metadata.name
                try:
                    items_dict['pod_appname'] = items.metadata.labels['k8s-app']
                except Exception as e:
                    items_dict['pod_appname'] = items.metadata.labels['component']
                items_dict['pod_namespace'] = items.metadata.namespace
                items_dict['pod_creatime'] = str(items.metadata.creation_timestamp.astimezone(pytz.timezone('Asia/Shanghai')))
                items_dict['host_ip'] = items.status.host_ip
                items_dict['pod_ip'] = items.status.pod_ip
                items_dict['img_rel'] = ",".join([x.image for x in items.spec.containers])
                items_dict['pod_status'] = items.status.phase
                items_dict['container_name_list'] = ','.join([container.name for container in items.spec.containers])
                pod_list.append(items_dict)

        all_numbers = len(pod_list)
        if all_numbers != 0:
            paginator = Paginator(pod_list,limit)
            contacts = paginator.page(page)
            list123 = contacts.object_list
        else:
            list123 = []
        return JsonResponse({'status': 200, 'message': "查询成功.", 'items': list123, 'total': all_numbers,
                             'query_dict': query_dict, 'selected_ns': pod_nspace})


class ContainerlogView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request):
        pod_nspace = request.GET.get('pod_nspace')
        pod_cluster = request.GET.get('pod_cluster')
        pod_name = request.GET.get('pod_name')
        pod_container = request.GET.get('pod_container')
        tail_lines = request.GET.get('tail_lines', None)
        api_host = KubeEnv.objects.get(k8s_ident=pod_cluster).k8sapi
        api_token = KubeEnv.objects.get(k8s_ident=pod_cluster).k8sapi_token
        kubeclient = KubernetesAPI(api_host=api_host,token=api_token)
        query_args = dict()
        query_args['container'] = pod_container
        query_args['timestamps'] = True
        # query_args['limit_bytes'] = 2000
        if tail_lines:
            query_args['tail_lines'] = tail_lines
        try:
            container_logs = kubeclient.CoreV1Api.read_namespaced_pod_log(name=pod_name, namespace=pod_nspace, **query_args)
            return JsonResponse({'status': 200, 'message': "查询成功", 'data': container_logs})

        except Exception as e:
            print(e)
            return JsonResponse({'status': 500, 'message': "查询失败", 'data': str(e)})


@require_websocket
def terminal_start(request, namespace, pod_name, container_name, k8s_apiport, usertoken):
    api_host = KubeEnv.objects.get(k8s_ident=k8s_apiport).k8sapi
    api_token = KubeEnv.objects.get(k8s_ident=k8s_apiport).k8sapi_token
    kubeclient = KubernetesAPI(api_host=api_host, token=api_token)


    try:
        valid_data = VerifyJSONWebTokenSerializer().validate({'token': usertoken})
        user = valid_data['user']
        username = user
        if settings.APPENV != 'beta':
            kafka_btserver = settings.KAFKA_BTSERFVER
            kafka_topic = settings.KAFKA_TOPIC
            kh = KafkaHandler(kafka_btserver, kafka_topic)
            logger = logging.getLogger(__name__)
            logger.addHandler(kh)
            logger.setLevel(logging.DEBUG)
    except Exception as e:
        return JsonResponse({"validation error", e})
    if KubePermission.objects.filter(user_name=username,kube_namespace=namespace).exists() or\
            UserProfile.objects.filter(username=username).first().is_superuser:

        try:
            container_stream = kubeclient.terminal_start(pod_name=pod_name, namespace=namespace, container=container_name)
            log_buffer = ''
        except Exception as err:
            print('Connect container error: {}'.format(err))
            request.websocket.close()
            return

        kub_stream = K8SStreamThread(request, container_stream)
        kub_stream.start()
        try:
            while not request.websocket.is_closed():
                try:
                    message = request.websocket.wait()
                    if message is not None:
                        container_stream.write_stdin(message.decode())
                        if settings.APPENV != 'beta':
                            if message == b'\r':
                                logdata = {"tags": kafka_topic,
                                           "logdate": str(datetime.now()),
                                           "namespace": namespace,
                                           "pod": pod_name,
                                           "container": container_name,
                                           "user": username.username,
                                           "command": log_buffer}
                                log_buffer = ''
                            else:
                                log_buffer += message.decode()
                except Exception as err:
                    request.websocket.close()
                    container_stream.close()
                    print('Connect container error: {}'.format(err))
        except Exception as err:
            print('Connect container error: {}'.format(err))
            container_stream.write_stdin('exit\r')
            request.websocket.close()
            container_stream.close()
        finally:
            request.websocket.close()
            container_stream.close()
    else:
        pass
