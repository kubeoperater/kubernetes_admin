from utils.kube import KubernetesAPI
from kubernetes.client import CustomObjectsApi
import json
api_address = 'https://10.10.216.180:6443'
api_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6Ii1YaFlEd3ZNZU5heDBRY2YwQ0gwV3lPcEg2TFhSR2xkOVFSSnJrN0JPWUUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuLXI3eG1sIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiI2MTIxNTE3OC0wM2NkLTRkZGQtYjQ1NS0yMDE4NDM0YTI2NzYiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4tdXNlciJ9.m5lP7CulAEEUgE_AD6U6UzCPVdt4KFEd-CsmH0puRz0qv1kkz_yKuyX53rhCw5VuNWTgdCgPJ8xUc_qxnOkK4czPraqOv8TsxZDpYXeihewH3yJ3C3szFfOtkyeitDWsI6n1iPCTb_drZs-xyoW7UgE4IO2hlilOtgtG3-FdrBPBO5JACoSUDq4FWpYDpHNEaELfymWkYahqPufiTwTvWnuGoT9IAl8YBAtHM4m5pQTPsNNk0TZ43zxLv8Lz3BvsAIbNsXUqrOr5HoqazJVzRQs60MHSIPSFAfPPklyaViUFgoaf_EXPr97A3IABWme2R88FNU4VTivqNhZBxcocew'
kube_client = KubernetesAPI(api_host=api_address, token=api_token)
cust = kube_client.CustomObjectsApi
# CustomObjectsApi(kube_client).list_cluster_custom_object('metrics.k8s.io', 'v1beta1', 'nodes')
print(json.dumps(cust.list_cluster_custom_object('metrics.k8s.io', 'v1beta1', 'pods')))