from utils.kube import KubernetesAPI

api_address = 'https://10.255.56.250:6444'
api_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkYXNoYm9hcmQtdG9rZW4temI0azciLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGFzaGJvYXJkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNTg3MTE4NGUtOTllYi0xMWU4LWIzZGEtYzgxZjY2YzJiZThiIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmRhc2hib2FyZCJ9.Ab_D8x0oXXN-q-ErzbNzVtlOwymynpfpgMR2AumtWQv5YqQkRAv20e98l2DfjHzn7GmcQWX5xALszNjMQvzrZCNSvuwLC8H4m60ctq98wTzH_uKz72qkhLqJL93lqRj9FcQ6UfWBstW4L96ZsragbYX3JV1fBXNmdU6ZVZbzUCGqcjf7fgDBNJ9_JDDZ4SM1xH6UaI_dKLzm-xNtE2FtdoBeUZILmyG_bcFqNrtzi57GyWIH-AW4mHtiIrrm4eo-2p8uv3-A_Ur5jJpV8YFjfPc81WN3f1xLWGH19uKkCgkIc1xjMD1O479LFOn4TtvsGf0yh5KV9wgMbvIjaUPtVw'
kube_client = KubernetesAPI(api_host=api_address, token=api_token)


def getpodinfo(nodename):
    pod_list_all = kube_client.client_core_v1.list_pod_for_all_namespaces(field_selector="spec.nodeName=%s" % nodename)\
        .items
    run_count = 0
    wrong_count = 0

    for pod_info in pod_list_all:
        if pod_info.status.phase == 'Running':
            run_count += 1
        else:
            wrong_count += 1
    return len(pod_list_all),run_count,wrong_count


def getnodeinfo():
    nodeset = kube_client.client_core_v1.list_node().items
    node_list = list()
    for items in nodeset:
        print(items)
    #     node_name = str(items.metadata.name)
    #     node_dict = dict()
    #     node_dict['labels'] = items.metadata.labels
    #     node_dict['pod_cidr'] = items.spec.pod_cidr
    #     node_dict['node_name'] = node_name
    #     node_dict['node_info'] = items.status.node_info
    #     pod_num, run_count,wrong_count = getpodinfo(node_name)
    #     node_dict['pod_num'] = pod_num
    #     node_dict['run_count'] = run_count
    #     node_dict['wrong_count'] = wrong_count
    #     node_list.append(node_dict)
    # print(node_list)


getnodeinfo()