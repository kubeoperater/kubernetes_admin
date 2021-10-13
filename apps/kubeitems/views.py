from rest_framework.views import APIView
from utils.kube import KubernetesAPI
from django.http import JsonResponse
from kubeadmin.models import KubeEnv
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
import pytz
import json
from .models import Projectlist
from kubeadmin.models import KubePermission
from django.core.paginator import Paginator
from utils.harborapi import HarborApi
from django.conf import settings
from .tasks import deploy_dp_app,mkgfsvolume, deploy_svc
from django_celery_results.models import TaskResult


class ProjectchangeView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.META.get('CONTENT_TYPE', '') == 'application/x-www-form-urlencoded':
            request_body = request.POST
        else:
            request_body = json.loads(request.body)
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        data = {'token': token}
        try:
            valid_data = VerifyJSONWebTokenSerializer().validate(data)
            user = valid_data['user']
            username = user.username
        except Exception as e:
            return JsonResponse({"validation error", e})
        # #project_env
        project_name = request_body['project_name']
        project_namespace = request_body['project_namespace']
        deploy_type = request_body['deploy_type']
        project_port = request_body['project_port']
        model_action = request_body['action']
        if model_action == 'create':
            imagepullsecrets = 'harbor'
            project_replicas = request_body['project_replicas']
            project_image = request_body['project_image']
            project_image_url = settings.HARBORURL + project_namespace + '/' + project_name + ":" + project_image
            if project_name and project_namespace and project_image:
                harbor_client = HarborApi(settings.HARBORHOST, settings.HARBORUSER, settings.HARBORPASS)
                harbor_client.login_get_session_id()
                status, result = harbor_client.tags_info(project_namespace + '/' + project_name, project_image)
                if type(result) != dict:
                    result = json.loads(result.decode())
                if 'code' in result:
                    return JsonResponse(dict(status=500, message=str(result['message']).replace(
                        'resource: ', settings.HARBORURL)))
            try:
                create_obj = Projectlist.objects.create(project_user=username,
                                                         project_port=project_port,
                                                         deploy_type=deploy_type,
                                                         project_image=project_image_url,
                                                         project_replicas=project_replicas,
                                                         project_name=project_name,
                                                         project_namespace=project_namespace,
                                                         imagepullsecrets=imagepullsecrets)
                return JsonResponse ({'status': 200, 'message': "创建成功.", 'id': create_obj.id})
            except Exception as e:
                return JsonResponse ({'status': 500, 'message': str(e)})

        elif model_action == 'update':
            project_status = request_body['project_status']
            try:
                update_obj = Projectlist.objects.filter(project_name=project_name).update(
                    project_status=project_status,
                    project_namespace=project_namespace,
                    project_port=project_port,
                    deploy_type=deploy_type)
                return JsonResponse({'status': 200, 'message': "创建成功.", 'id': update_obj})
            except Exception as e:
                return JsonResponse({'status': 500, 'message': str(e)})


class ProjectListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        data = {'token': token}
        try:
            valid_data = VerifyJSONWebTokenSerializer().validate(data)
            user = valid_data['user']
            username = user
        except Exception as e:
            return JsonResponse({"validation error", e})
        cluster_alias = request.GET.get('project_cluster')
        project_name = request.GET.get('project_name')
        pro_nspace = request.GET.get('pro_nspace')
        deploy_type = request.GET.get('deploy_type')
        project_status = request.GET.get('project_status')
        page = request.GET.get('page')
        limit = request.GET.get('limit')
        filter_dict = dict()

        if pro_nspace:
            filter_dict['project_namespace'] = pro_nspace
        if deploy_type:
            filter_dict['deploy_type'] = deploy_type
        if project_status:
            filter_dict['project_status'] = project_status
        if UserProfile.objects.filter(username=username).first().is_superuser:
            api_address = KubeEnv.objects.filter (k8s_ident=cluster_alias).values('k8sapi')[0]['k8sapi']
            api_token = KubeEnv.objects.filter(k8s_ident=cluster_alias).values('k8sapi_token')[0]['k8sapi_token']
            kube_client = KubernetesAPI(api_host=api_address, token=api_token)
            namespace_list = [ item.metadata.name for item in kube_client.client_core_v1.list_namespace(timeout_seconds=10).items ]

        else:
            try:
                permission_set = KubePermission.objects.filter(user_name=username).values('kube_namespace')
                namespace_list = list(set([x['kube_namespace'] for x in permission_set]))
            except Exception as e:
                return JsonResponse(dict(status=403, message="该用户没有命名空间权限"))
        if project_name:
            filter_dict['project_name'] = project_name
        project_list = list(Projectlist.objects.filter(**filter_dict).values())
        all_numbers = len(project_list)
        if all_numbers != 0:
            paginator = Paginator(project_list, limit)
            contacts = paginator.page(page)
            list123 = contacts.object_list
        else:
            list123 = []
        return JsonResponse(dict(status=200, all_project=project_list, items=list123, total=all_numbers, selected_ns=pro_nspace,
                                 namespace_dict=namespace_list))


class ProjectDeployView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.META.get('CONTENT_TYPE', '') == 'application/x-www-form-urlencoded':
            request_body = request.POST
        else:
            request_body = json.loads(request.body)
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        data = {'token': token}
        try:
            valid_data = VerifyJSONWebTokenSerializer().validate(data)
            user = valid_data['user']
            username = user.username
        except Exception as e:
            return JsonResponse({"validation error", e})
        cluster_alias = request_body['cluster_alias']
        project_name = request_body['project_name']
        project_namespace = request_body['project_namespace']
        project_replicas = request_body['project_replicas']
        deploy_type = request_body['deploy_type']
        project_port = int(request_body['project_port'])
        project_image = request_body['project_image']
        project_release = str(project_image).split(':')[-1]
        volume_task_id = mkgfsvolume.delay(project_name, project_namespace,cluster_alias).task_id
        deploy_id = deploy_dp_app.delay(project_name,project_namespace,cluster_alias,deploy_type,project_image,project_port,project_release,project_replicas,volume_task_id).task_id
        svc_id = deploy_svc.delay(project_name,project_namespace,project_port,cluster_alias,deploy_id).task_id
        Projectlist.objects.filter(project_name=project_name,project_namespace=project_namespace).update(project_status='PEDDING',
                                                                                                         project_create_id=deploy_id,
                                                                                                         project_volumecreate_id=volume_task_id,
                                                                                                         project_svc_id=svc_id)
        return JsonResponse(dict(status=200, message='deploy ok.', deploy_id=deploy_id, svc_id=svc_id,
                                 volume_task_id=volume_task_id))


class ProjectTaskView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        data = {'token': token}
        try:
            valid_data = VerifyJSONWebTokenSerializer().validate(data)
            user = valid_data['user']
            username = user
        except Exception as e:
            return JsonResponse({"validation error", e})
        try:
            project_name = request.GET.get('project_name')
            project_namespace = request.GET.get('project_namespace')
            project_volumecreate_id = Projectlist.objects.filter(project_name=project_name,
                                                                 project_namespace=project_namespace).values(
                'project_volumecreate_id').first()['project_volumecreate_id']
            project_create_id = Projectlist.objects.filter(project_name=project_name,
                                                           project_namespace=project_namespace).values(
                'project_create_id').first()['project_create_id']
            project_svc_id = Projectlist.objects.filter(project_name=project_name,
                                                            project_namespace=project_namespace).values(
                'project_svc_id').first()['project_svc_id']
            project_volume_message = \
                str(TaskResult.objects.filter(task_id=project_volumecreate_id).values('result').first()['result'])
            project_message = \
                TaskResult.objects.filter(task_id=project_create_id).values('result').first()['result']
            project_svc_message = \
                TaskResult.objects.filter(task_id=project_svc_id).values('result').first()['result']
            return JsonResponse(dict(status=200, project_message=project_message,project_volume_message=project_volume_message,
                                     project_svc_message=project_svc_message))
        except Exception as e:
            print(e)
            return JsonResponse(dict(status=500, message=str(e)))
