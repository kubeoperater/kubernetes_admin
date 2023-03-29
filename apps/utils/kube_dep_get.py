from utils.kube import KubernetesAPI
from kubernetes.client import CustomObjectsApi
import json
api_address = 'https://10.10.216.180:6443'
api_token = ''
kube_client = KubernetesAPI(api_host=api_address, token=api_token)
cust = kube_client.CustomObjectsApi
# CustomObjectsApi(kube_client).list_cluster_custom_object('metrics.k8s.io', 'v1beta1', 'nodes')
print(json.dumps(cust.list_cluster_custom_object('metrics.k8s.io', 'v1beta1', 'pods')))