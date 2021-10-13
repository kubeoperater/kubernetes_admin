from rest_framework.views import APIView
from utils.kube import KubernetesAPI
from django.http import JsonResponse
from kubeadmin.models import KubeEnv
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
import json
from utils.unit_reduce import mem_format,cpu_usage
from .models import NodeLabels


class KubenodeView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,request):
        node_cluster = request.GET.get('node_cluster')
        page = request.GET.get('page')
        limit = request.GET.get('limit')
        node_label = request.GET.get('node_label')
        nodename = request.GET.get('nodename')

        if node_cluster:
            api_address = KubeEnv.objects.filter(k8s_ident=node_cluster).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=node_cluster).values('k8sapi_token')[0]['k8sapi_token']
        else:
            return JsonResponse({'status': 403, 'message': "该用户集群权限"})
        kube_client = KubernetesAPI(api_host=api_address, token=api_token)
        query_dict = {}
        if node_label:
            query_dict['label_selector'] = 'appgroup={}'.format(node_label)
        if nodename:
            query_dict['field_selector'] = 'metadata.name={}'.format(nodename)

        nodeset = kube_client.client_core_v1.list_node(**query_dict).items
        node_list2 = [item.metadata.name for item in kube_client.client_core_v1.list_node().items]
        node_list = list()
        for items in nodeset:
            nodeinfo = dict()
            nodeinfo['machine_id'] = items.status.node_info.machine_id
            nodeinfo['kernel_version'] = items.status.node_info.kernel_version
            nodeinfo['kube_proxy_version'] = items.status.node_info.kube_proxy_version
            nodeinfo['kubelet_version'] = items.status.node_info.kubelet_version
            nodeinfo['operating_system'] = items.status.node_info.operating_system
            nodeinfo['os_image'] = items.status.node_info.os_image
            nodeinfo['container_runtime_version'] = items.status.node_info.container_runtime_version
            try :
                nodestats = kube_client.client_core_v1.connect_get_node_proxy_with_path(items.metadata.name, path='stats')
                nodeusageget = json.loads(nodestats.replace("'", "\"").
                                        replace("True", "\"True\"").
                                        replace("False", "\"False\""))
                nodecreatime = nodeusageget['spec']['creation_time']
                nodeusage = nodeusageget['stats'][0]
                nodeusage_cpu = cpu_usage(int(nodeusage['cpu']['usage']['total']),
                                          int(nodeusage['cpu']['usage']['system']),
                                          int(nodeusage['cpu']['usage']['user']))

                nodeusage_mem = mem_format(int(nodeusage['memory']['working_set'])) + ' / ' + mem_format(int(nodeusageget['spec']['memory']['limit']))
            except:
                nodeusage_mem = ""
                nodeusage_cpu = ""
                nodecreatime = ""
            pod_list_all = kube_client.client_core_v1.list_pod_for_all_namespaces(
                field_selector="spec.nodeName=%s" % items.metadata.name) \
                .items
            run_count = 0
            wrong_count = 0
            for pod_info in pod_list_all:
                if pod_info.status.phase == 'Running':
                    run_count += 1
                else:
                    wrong_count += 1
            node_dict = dict()
            node_dict['labels'] = items.metadata.labels
            node_dict['pod_cidr'] = items.spec.pod_cidr
            node_dict['node_name'] = items.metadata.name
            node_dict['node_info'] = nodeinfo
            node_dict['nodeusage_mem'] = nodeusage_mem
            node_dict['nodeusage_cpu'] = nodeusage_cpu
            node_dict['run_count'] = run_count
            node_dict['wrong_count'] = wrong_count
            node_dict['pod_num'] = len(pod_list_all)
            node_dict['nodecreatime'] = nodecreatime
            node_list.append(node_dict)
        all_numbers = len(node_list)
        if all_numbers != 0:
            paginator = Paginator(node_list, limit)
            contacts = paginator.page(page)
            list123 = contacts.object_list
        else:
            list123 = []
        labels_list = [item.groupident for item in NodeLabels.objects.all()]
        return JsonResponse({'status': 200, 'message': "查询成功.", 'item': list123, 'labels_list': labels_list,
                             'node_list': node_list2,
                             'total': all_numbers})
