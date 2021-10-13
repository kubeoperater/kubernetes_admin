from django.shortcuts import render
from kubernetes import client
from kubernetes.stream import stream
from kubernetes.client import CustomObjectsApi
import urllib3
urllib3.disable_warnings()
import threading
# Create your views here.


class KubernetesAPI(object):

    def __init__(self, api_host, token):
        kub_conf = client.Configuration()
        kub_conf.host = api_host
        kub_conf.verify_ssl = False
        client.Configuration.set_default(kub_conf)
        kub_conf.api_key = {"authorization": "Bearer " + token}
        # kub_conf.debug = True
        self.V1beta1Deployment = client.V1Deployment()
        self.api_client = client.ApiClient(configuration=kub_conf)
        self.client_core_v1 = client.CoreV1Api(api_client=self.api_client)
        self.client_apps_v1 = client.AppsV1Api(api_client=self.api_client)
        self.CoreV1Api = client.CoreV1Api(api_client=self.api_client)
        self.LogsApi = client.LogsApi(api_client=self.api_client)
        self.client_extensions_v1 = client.ExtensionsV1beta1Api(
            api_client=self.api_client)
        self.CustomObjectsApi = CustomObjectsApi(client.ApiClient(configuration=kub_conf))
        self.api_dict = {}

    def __getattr__(self, item):
        if item in self.api_dict:
            return self.api_dict[item]
        if hasattr(client, item) and callable(getattr(client, item)):
            self.api_dict[item] = getattr(client, item)(
                api_client=self.api_client)
            return self.api_dict[item]

    def terminal_start(self, namespace, pod_name, container):
        command = [
            "/bin/sh",
            "-c",
            'TERM=xterm-256color; export TERM; [ -x /bin/bash ] '
            '&& ([ -x /usr/bin/script ] '
            '&& /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) '
            '|| exec /bin/sh']

        container_stream = stream(
            self.client_core_v1.connect_get_namespaced_pod_exec,
            name=pod_name,
            namespace=namespace,
            container=container,
            command=command,
            stderr=True, stdin=True,
            stdout=True, tty=True,
            _preload_content=False,
        )

        return container_stream


class K8SStreamThread(threading.Thread):

    def __init__(self, ws, container_stream):
        super(K8SStreamThread, self).__init__()
        self.ws = ws.websocket
        self.stream = container_stream

    def run(self):
        while not self.ws.is_closed():
            if not self.stream.is_open():
                print('container stream closed')
                self.ws.close()
            else:
                try:
                    if self.stream.peek_stdout():
                        stdout = str(self.stream.read_stdout())
                        self.ws.send(stdout.encode())
                    if self.stream.peek_stderr():
                        stderr = str(self.stream.read_stderr())
                        self.ws.send(stderr.encode())
                except Exception as err:
                    print('Connect container error: {}'.format(err))
                    self.ws.close()
                    self.stream.close()
                    break
