from utils.kube import KubernetesAPI
from pprint import pprint

api_address = 'https://10.255.56.250:6444'
api_token = ''
kube_client = KubernetesAPI(api_host=api_address, token=api_token)
dep_namespace = 'default'
dep_name = 'nginx'
patch = {"spec": {"replicas": 1}}
patch_status = kube_client.client_apps_v1.patch_namespaced_deployment_scale(name=dep_name,namespace=dep_namespace,
                                                                            body=patch,
                                                                            pretty=True)
pprint(patch_status.status)