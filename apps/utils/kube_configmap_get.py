from utils.kube import KubernetesAPI
import pytz
from pprint import pprint
import json

api_address = 'https://10.255.56.250:6444'
api_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkYXNoYm9hcmQtdG9rZW4temI0azciLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGFzaGJvYXJkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNTg3MTE4NGUtOTllYi0xMWU4LWIzZGEtYzgxZjY2YzJiZThiIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmRhc2hib2FyZCJ9.Ab_D8x0oXXN-q-ErzbNzVtlOwymynpfpgMR2AumtWQv5YqQkRAv20e98l2DfjHzn7GmcQWX5xALszNjMQvzrZCNSvuwLC8H4m60ctq98wTzH_uKz72qkhLqJL93lqRj9FcQ6UfWBstW4L96ZsragbYX3JV1fBXNmdU6ZVZbzUCGqcjf7fgDBNJ9_JDDZ4SM1xH6UaI_dKLzm-xNtE2FtdoBeUZILmyG_bcFqNrtzi57GyWIH-AW4mHtiIrrm4eo-2p8uv3-A_Ur5jJpV8YFjfPc81WN3f1xLWGH19uKkCgkIc1xjMD1O479LFOn4TtvsGf0yh5KV9wgMbvIjaUPtVw'
kube_client = KubernetesAPI(api_host=api_address, token=api_token)
project_namespace = 'default'
project_name = 'nginx'
project_release = '201912121320'
project_img = "hub-dev.fengjr.com/default/nginx:201912121320"
project_port = 80
project_pvc = project_name + '-' + project_namespace + '-pvc'
project_pv = project_name + '-' + project_namespace + '-pv'
project_volume = project_name + '-' + project_namespace + '-volume'
project_harbor = 'harbor'
state_body = {"apiVersion": "apps/v1",
              "kind": "StatefulSet",
              "metadata": {
                  "labels": {
                      "k8s-app": project_name
                  },
                  "name": project_name,
                  "namespace": project_namespace,
              },
              "spec": {
                  "replicas": 2,
                  "selector": {
                      "matchLabels": {
                          "k8s-app": project_name
                      }
                  },
                  "serviceName": project_name,
                  "template": {
                      "metadata": {
                          "labels": {
                              "k8s-app": project_name
                          }
                      },
                      "spec": {
                          "affinity": {
                              "podAntiAffinity": {
                                  "requiredDuringSchedulingIgnoredDuringExecution": [{
                                      "labelSelector": {
                                          "matchExpressions": [{
                                              "key": "k8s-app",
                                              "operator": "In",
                                              "values": [project_name]
                                          }]
                                      },
                                      "topologyKey": "kubernetes.io/hostname"
                                  }]
                              }
                          },
                          "containers": [{
                              "env": [{
                                  "name": "APPNAME",
                                  "value": project_name
                              },
                                  {
                                      "name": "release_version",
                                      "value": project_release
                                  }
                              ],
                              "image": project_img,
                              "imagePullPolicy": "Always",
                              "livenessProbe": {
                                  "failureThreshold": 3,
                                  "initialDelaySeconds": 15,
                                  "periodSeconds": 20,
                                  "successThreshold": 1,
                                  "tcpSocket": {
                                      "port": project_port
                                  },
                                  "timeoutSeconds": 1
                              },
                              "name": project_name,
                              "ports": [{
                                  "containerPort": project_port,
                                  "protocol": "TCP"
                              }],
                              "readinessProbe": {
                                  "failureThreshold": 3,
                                  "initialDelaySeconds": 5,
                                  "periodSeconds": 10,
                                  "successThreshold": 1,
                                  "tcpSocket": {
                                      "port": project_port
                                  },
                                  "timeoutSeconds": 1
                              },
                              "volumeMounts": [{
                                  "mountPath": "/applog",
                                  "name": "logdir"
                              }]
                          },
                              {
                                  "env": [{
                                      "name": "appname",
                                      "value": project_name
                                  }, {
                                      "name": "release_version",
                                      "value": project_release
                                  },
                                      {
                                          "name": "MY_NODE_NAME",
                                          "valueFrom": {
                                              "fieldRef": {
                                                  "apiVersion": "v1",
                                                  "fieldPath": "spec.nodeName"
                                              }
                                          }
                                      },
                                      {
                                          "name": "MY_POD_NAME",
                                          "valueFrom": {
                                              "fieldRef": {
                                                  "apiVersion": "v1",
                                                  "fieldPath": "metadata.name"
                                              }
                                          }
                                      },
                                      {
                                          "name": "MY_POD_NAMESPACE",
                                          "valueFrom": {
                                              "fieldRef": {
                                                  "apiVersion": "v1",
                                                  "fieldPath": "metadata.namespace"
                                              }
                                          }
                                      },
                                      {
                                          "name": "MY_POD_IP",
                                          "valueFrom": {
                                              "fieldRef": {
                                                  "apiVersion": "v1",
                                                  "fieldPath": "status.podIP"
                                              }
                                          }
                                      }
                                  ],
                                  "image": "harbor-pro.fengjr.com/base/filebeat-kafka:v1.6",
                                  "imagePullPolicy": "Always",
                                  "name": "filebeat-agent",
                                  "volumeMounts": [{
                                      "mountPath": "/export/log/",
                                      "name": "logdir"
                                  },
                                      {
                                          "mountPath": "/opt/",
                                          "name": "filebeat-yaml"
                                      }
                                  ]
                              }
                          ],
                          "dnsConfig": {
                              "nameservers": ["10.10.0.200", "10.10.0.11"],
                              "options": [{
                                  "name": "ndots",
                                  "value": "2"
                              }, {
                                  "name": "edns0"
                              }]
                          },
                          "dnsPolicy": "ClusterFirst",
                          "imagePullSecrets": [{
                              "name": project_harbor
                          }],
                          "restartPolicy": "Always",
                          "schedulerName": "default-scheduler",
                          "securityContext": {},
                          "terminationGracePeriodSeconds": 10,
                          "volumes": [{
                              "name": "logdir",
                              "persistentVolumeClaim": {
                                  "claimName": project_pvc
                              }
                          }, {
                              "configMap": {
                                  "defaultMode": 420,
                                  "name": "filebeat-v1"
                              },
                              "name": "filebeat-yaml"
                          }]
                      }
                  }}}
pv_body = {
    "apiVersion": "v1",
    "kind": "PersistentVolume",
    "metadata": {
        "finalizers": [
            "kubernetes.io/pv-protection"
        ],
        "labels": {
            "type": "glusterfs"
        },
        "name": project_pv,
    },
    "spec": {
        "accessModes": [
            "ReadWriteMany"
        ],
        "capacity": {
            "storage": "100Gi"
        },
        "glusterfs": {
            "endpoints": "glusterfs-cluster",
            "path": project_volume
        },
        "persistentVolumeReclaimPolicy": "Recycle",
        "storageClassName": project_pv,
        "volumeMode": "Filesystem"
    },
}
pvc_body = {
    "apiVersion": "v1",
    "kind": "PersistentVolumeClaim",
    "metadata": {
        "finalizers": [
            "kubernetes.io/pvc-protection"
        ],
        "name": project_pvc,
        "namespace": project_namespace,
    },
    "spec": {
        "accessModes": [
            "ReadWriteMany"
        ],
        "resources": {
            "requests": {
                "storage": "100Gi"
            }
        },
        "storageClassName": project_pv,
        "volumeMode": "Filesystem",
        "volumeName": project_pv
    },
}
dep_body = {"apiVersion": "apps/v1",
              "kind": "Deployment",
              "metadata": {
                  "labels": {
                      "k8s-app": project_name
                  },
                  "name": project_name,
                  "namespace": project_namespace,
              },
              "spec": {
                  "replicas": 2,
                  "selector": {
                      "matchLabels": {
                          "k8s-app": project_name
                      }
                  },
                  "serviceName": project_name,
                  "template": {
                      "metadata": {
                          "labels": {
                              "k8s-app": project_name
                          }
                      },
                      "spec": {
                          "affinity": {
                              "podAntiAffinity": {
                                  "requiredDuringSchedulingIgnoredDuringExecution": [{
                                      "labelSelector": {
                                          "matchExpressions": [{
                                              "key": "k8s-app",
                                              "operator": "In",
                                              "values": [project_name]
                                          }]
                                      },
                                      "topologyKey": "kubernetes.io/hostname"
                                  }]
                              }
                          },
                          "containers": [{
                              "env": [{
                                  "name": "APPNAME",
                                  "value": project_name
                              },
                                  {
                                      "name": "release_version",
                                      "value": project_release
                                  }
                              ],
                              "image": project_img,
                              "imagePullPolicy": "Always",
                              "livenessProbe": {
                                  "failureThreshold": 3,
                                  "initialDelaySeconds": 15,
                                  "periodSeconds": 20,
                                  "successThreshold": 1,
                                  "tcpSocket": {
                                      "port": project_port
                                  },
                                  "timeoutSeconds": 1
                              },
                              "name": project_name,
                              "ports": [{
                                  "containerPort": project_port,
                                  "protocol": "TCP"
                              }],
                              "readinessProbe": {
                                  "failureThreshold": 3,
                                  "initialDelaySeconds": 5,
                                  "periodSeconds": 10,
                                  "successThreshold": 1,
                                  "tcpSocket": {
                                      "port": project_port
                                  },
                                  "timeoutSeconds": 1
                              },
                              "volumeMounts": [{
                                  "mountPath": "/applog",
                                  "name": "logdir"
                              }]
                          },
                              {
                                  "env": [{
                                      "name": "appname",
                                      "value": project_name
                                  }, {
                                      "name": "release_version",
                                      "value": project_release
                                  },
                                      {
                                          "name": "MY_NODE_NAME",
                                          "valueFrom": {
                                              "fieldRef": {
                                                  "apiVersion": "v1",
                                                  "fieldPath": "spec.nodeName"
                                              }
                                          }
                                      },
                                      {
                                          "name": "MY_POD_NAME",
                                          "valueFrom": {
                                              "fieldRef": {
                                                  "apiVersion": "v1",
                                                  "fieldPath": "metadata.name"
                                              }
                                          }
                                      },
                                      {
                                          "name": "MY_POD_NAMESPACE",
                                          "valueFrom": {
                                              "fieldRef": {
                                                  "apiVersion": "v1",
                                                  "fieldPath": "metadata.namespace"
                                              }
                                          }
                                      },
                                      {
                                          "name": "MY_POD_IP",
                                          "valueFrom": {
                                              "fieldRef": {
                                                  "apiVersion": "v1",
                                                  "fieldPath": "status.podIP"
                                              }
                                          }
                                      }
                                  ],
                                  "image": "hub-dev.fengjr.com/base/filebeat-kafka:v1.5",
                                  "imagePullPolicy": "Always",
                                  "name": "filebeat-agent",
                                  "volumeMounts": [{
                                      "mountPath": "/export/log/",
                                      "name": "logdir"
                                  },
                                      {
                                          "mountPath": "/opt/",
                                          "name": "filebeat-yaml"
                                      }
                                  ]
                              }
                          ],
                          "dnsConfig": {
                              "nameservers": ["10.10.0.200", "10.10.0.11"],
                              "options": [{
                                  "name": "ndots",
                                  "value": "2"
                              }, {
                                  "name": "edns0"
                              }]
                          },
                          "dnsPolicy": "ClusterFirst",
                          "imagePullSecrets": [{
                              "name": project_harbor
                          }],
                          "restartPolicy": "Always",
                          "schedulerName": "default-scheduler",
                          "securityContext": {},
                          "terminationGracePeriodSeconds": 10,
                          "volumes": [{
                              "name": "logdir",
                              "persistentVolumeClaim": {
                                  "claimName": project_pvc
                              }
                          }, {
                              "configMap": {
                                  "defaultMode": 420,
                                  "name": "filebeat-v1"
                              },
                              "name": "filebeat-yaml"
                          }]
                      }
                  }}}
deploy_status = kube_client.client_apps_v1.create_namespaced_deployment(namespace=project_namespace,body=dep_body)
# pv_status = kube_client.client_core_v1.create_persistent_volume(body=pv_body)
# pvc_status = kube_client.client_core_v1.create_namespaced_persistent_volume_claim(namespace=project_namespace,body=pvc_body)
# state_status = kube_client.client_apps_v1.create_namespaced_stateful_set(namespace=project_namespace,body=state_body)
print(str(deploy_status))