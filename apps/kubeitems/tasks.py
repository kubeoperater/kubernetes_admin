# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.conf import settings
from utils.kube import KubernetesAPI
from kubeadmin.models import KubeEnv
from django_celery_results.models import TaskResult
import paramiko
from time import sleep
from .models import Projectlist
from .models import HostPassTable



@shared_task()
def mkgfsvolume(project_name, project_namespace, cluster_alias):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        host_pass = HostPassTable.objects.filter(host_room=cluster_alias, host_user='root').values('host_pass').first ()[
            'host_pass']
        ssh_client.connect(hostname=settings.GLUSTER_VIP,password=host_pass, port=22, username='root')
        command = '/bin/bash /root/sh/create_volume_dir.sh {} {} {}'.format(settings.GLUSTER_ROOTPATH, project_namespace, project_name)
        stdin, stdout, stderr = ssh_client.exec_command(command=command, get_pty=True,timeout=300)
        result = stdout.read().decode()
        if stdout.channel.recv_exit_status() == 0:
            return result
        else:
            raise OSError(result)
    except Exception as e:
        raise OSError(str(e))
    finally:
        ssh_client.close()


@shared_task()
def deploy_dp_app(project_name,project_namespace,cluster_alias,deploy_type,project_image,project_port,project_release,project_replicas,volume_task_id):
    try:
        wait_count = 10
        while wait_count != 0:
            if TaskResult.objects.filter(task_id=volume_task_id):
                if TaskResult.objects.filter(task_id=volume_task_id).values('status')[0]['status'] in ['FAILURE','SUCCESS']:
                    wait_count = 0
            else:
                sleep(10)
                wait_count -= 1
        volume_status = TaskResult.objects.filter(task_id=volume_task_id).values('status')[0]['status']
        if volume_status == 'SUCCESS':
            api_address = KubeEnv.objects.filter(k8s_ident=cluster_alias).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=cluster_alias).values('k8sapi_token')[0]['k8sapi_token']
            kube_client = KubernetesAPI (api_host=api_address, token=api_token)
            project_pvc = project_name + '-' + project_namespace + '-pvc'
            project_pv = project_name + '-' + project_namespace + '-pv'
            project_volume = project_name + '-' + project_namespace + '-volume'
            project_harbor = 'harbor'
            filebeat_image = settings.FILEBEAT_IMAGE
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
                    "persistentVolumeReclaimPolicy": "Retain",
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
                    "persistentVolumeReclaimPolicy": "Retain",
                    "volumeName": project_pv
                },
            }
            try:
                kube_client.client_core_v1.create_persistent_volume(body=pv_body)
                kube_client.client_core_v1.create_namespaced_persistent_volume_claim (namespace=project_namespace,
                                                                                      body=pvc_body)
            except Exception as e:
                raise OSError(str(e))

            if deploy_type == 'statefulset':
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
                                  "replicas": int(project_replicas),
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
                                              "image": project_image,
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
                                              "resources": {
                                                  "limits": {
                                                      "cpu": "2",
                                                      "memory": "4096Mi"
                                                  },
                                                  "requests": {
                                                      "cpu": "1",
                                                      "memory": "2048Mi"
                                                  }
                                              },
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
                                                  "image": filebeat_image,
                                                  "imagePullPolicy": "Always",
                                                  "name": "filebeat-agent",
                                                  "resources": {
                                                      "limits": {
                                                          "cpu": "20m",
                                                          "memory": "400Mi"
                                                      },
                                                      "requests": {
                                                          "cpu": "10m",
                                                          "memory": "200Mi"
                                                      }
                                                  },
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
                                          "nodeSelector": {
                                                "appgroup": project_namespace
                                            },
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
                state_status = kube_client.client_apps_v1.create_namespaced_stateful_set(namespace=project_namespace,
                                                                                          body=state_body)
                Projectlist.objects.filter(project_name=project_name, project_namespace=project_namespace).update (
                    project_status='success')
                return str(state_status)
            elif deploy_type == 'deployment':
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
                                "replicas": int(project_replicas),
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
                                            "image": project_image,
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
                                            "resources": {
                                                "limits": {
                                                    "cpu": "2",
                                                    "memory": "4096Mi"
                                                },
                                                "requests": {
                                                    "cpu": "1",
                                                    "memory": "2048Mi"
                                                }
                                            },
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
                                                "image": filebeat_image,
                                                "resources": {
                                                    "limits": {
                                                        "cpu": "20m",
                                                        "memory": "400Mi"
                                                    },
                                                    "requests": {
                                                        "cpu": "10m",
                                                        "memory": "200Mi"
                                                    }
                                                },
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
                                        "nodeSelector": {
                                            "appgroup": project_namespace
                                        },
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
                deploy_status = kube_client.client_apps_v1.create_namespaced_deployment(namespace=project_namespace,
                                                                                         body=dep_body)
                Projectlist.objects.filter(project_name=project_name, project_namespace=project_namespace).update (
                    project_status='success')
                return str(deploy_status)
            else:
                Projectlist.objects.filter(project_name=project_name, project_namespace=project_namespace).update(
                    project_status='failed')
                raise ValueError("Missing the required parameter `deploy_type` when calling `deploy_dp_app`")
        else:
            Projectlist.objects.filter(project_name=project_name, project_namespace=project_namespace).update (
                project_status='failed')
            raise ValueError('volume create state is ' + volume_status)
    except Exception as e:
        Projectlist.objects.filter(project_name=project_name, project_namespace=project_namespace).update (
            project_status='failed')
        raise ValueError(str(e))


@shared_task()
def deploy_svc(project_name,project_namespace,apport,cluster_alias,deploy_task_id):
    try:
        wait_count = 10
        while wait_count != 0:
            if TaskResult.objects.filter(task_id=deploy_task_id):
                if TaskResult.objects.filter(task_id=deploy_task_id).values('status')[0]['status'] in ['FAILURE','SUCCESS']:
                    wait_count = 0
            else:
                sleep(10)
                wait_count -= 1
        deploy_status = TaskResult.objects.filter(task_id=deploy_task_id).values('status')[0]['status']
        if deploy_status == 'SUCCESS':
            api_address = KubeEnv.objects.filter(k8s_ident=cluster_alias).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=cluster_alias).values('k8sapi_token')[0]['k8sapi_token']
            kube_client = KubernetesAPI(api_host=api_address, token=api_token)
            svc_body = dict(apiVersion="v1", kind="Service", metadata={
                "labels": {
                    "k8s-app": project_name
                },
                "name": project_name,
            }, spec={
                "ports": [
                    {
                        "port": apport,
                        "protocol": "TCP",
                        "targetPort": apport
                    }
                ],
                "selector": {
                    "k8s-app": project_name
                },
                "type": "ClusterIP"
            })
            try:
                svc_status = kube_client.client_core_v1.create_namespaced_service(namespace=project_namespace,body=svc_body)
                return str(svc_status)
            except Exception as e:
                return str(e)
        else:
            Projectlist.objects.filter(project_name=project_name, project_namespace=project_namespace).update(
                project_status='failed')
            raise ValueError('部署应用状态为' + deploy_status)
    except Exception as e:
        Projectlist.objects.filter(project_name=project_name, project_namespace=project_namespace).update(
            project_status='failed')
        raise ValueError(str(e))
