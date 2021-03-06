from utils.kube import KubernetesAPI
api_address = 'https://10.255.56.250:6444'
api_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkYXNoYm9hcmQtdG9rZW4temI0azciLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGFzaGJvYXJkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNTg3MTE4NGUtOTllYi0xMWU4LWIzZGEtYzgxZjY2YzJiZThiIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmRhc2hib2FyZCJ9.Ab_D8x0oXXN-q-ErzbNzVtlOwymynpfpgMR2AumtWQv5YqQkRAv20e98l2DfjHzn7GmcQWX5xALszNjMQvzrZCNSvuwLC8H4m60ctq98wTzH_uKz72qkhLqJL93lqRj9FcQ6UfWBstW4L96ZsragbYX3JV1fBXNmdU6ZVZbzUCGqcjf7fgDBNJ9_JDDZ4SM1xH6UaI_dKLzm-xNtE2FtdoBeUZILmyG_bcFqNrtzi57GyWIH-AW4mHtiIrrm4eo-2p8uv3-A_Ur5jJpV8YFjfPc81WN3f1xLWGH19uKkCgkIc1xjMD1O479LFOn4TtvsGf0yh5KV9wgMbvIjaUPtVw'
kube_client = KubernetesAPI(api_host=api_address, token=api_token)
kube_svcset = kube_client.CoreV1Api.list_namespaced_service(namespace='default').items
for items in kube_svcset:
    print([str(i.port) + ":" + str(i.target_port) for i in items.spec.ports])
