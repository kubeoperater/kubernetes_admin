from django.contrib.auth.models import Group

from rest_framework.views import APIView
from django.http import JsonResponse
import json
from users.models import UserProfile
from rest_framework.permissions import IsAuthenticated
from kubeadmin.models import KubePermission, KubeEnv
from rest_framework_jwt.utils import jwt_decode_handler


def jwt_response_username_userid_token(token,user=None,request=None):

    """
    JWT登入验证成功之后 ，自定义处理返回数据
    :param token:
    :param user:
    :param request:
    :return:
    """
    if user:
        data = {
            'token': token,
            'username': user.username,
            'user_id': user.id,
            'status': 200
        }
    else:
        print('here')
        data = {
            'status': 500
        }
    return data

class UserinfoView(APIView):
    """
    用户信息
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        token = request.META['HTTP_AUTHORIZATION'].split('Bearer ')[1]
        username = jwt_decode_handler(token)['username']
        user_role = []
        userinfo_list = UserProfile.objects.filter(username=username)
        if len(userinfo_list) != 0:
            user_info = userinfo_list[0]
            if user_info.is_superuser:
                user_role.append('superuser')
            else:
                user_role.append('normal')
            try:
                k8s_permission_role = KubePermission.objects.filter(user_name=user_info)
                for permission_items in k8s_permission_role:
                    user_role.append(permission_items.kube_namespace + permission_items.kube_permis)
            except AttributeError as e:
                print(e)
                pass
            return JsonResponse({'status': 200, 'roles': user_role, 'name': user_info.username,
                                 'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'})
        else:
            return JsonResponse({'status': 50008, 'message': "登录凭证不正确."})

    def post(self,request):
        if request.META.get('CONTENT_TYPE', '') == 'application/x-www-form-urlencoded':
            request_body = request.POST
        else:
            request_body = json.loads(request.body)
        action_tag = request_body['action']
        is_superusers = str(request_body['is_superuser']).capitalize()
        username = request_body['username']
        email = request_body['email']
        gender = request_body['gender']
        if action_tag == 'update':
            user_id = request_body['id']
            UserProfile.objects.filter(id=user_id).update(is_superuser=is_superusers,username=username,email=email,gender=gender)
            return JsonResponse({'status': 200, 'id': user_id})
        elif action_tag == 'create':
            usercreate = UserProfile.objects.create(is_superuser=is_superusers, username=username,email=email,gender=gender)
            usercreate.save()
            return JsonResponse ({'status': 200, 'id': usercreate.id})
        elif action_tag == 'delete':
            user_id = request_body['id']
            UserProfile.objects.filter(id=user_id).delete()
            return JsonResponse({'status': 200, 'id': user_id})

class UserlogoutView(APIView):

    def post(self,request):
        return JsonResponse({'status': 200})


class UserlistView(APIView):
    """
    用户列表
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        all_userlist = list(UserProfile.objects.all().values())
        username = request.GET.get('user_name')
        userlevel = request.GET.get('userlevel')
        filter_dict = dict()
        if username:
            filter_dict['username'] = username
        if userlevel:
            if userlevel == 'superuser':
                filter_dict['is_superuser'] = str(True)
            else:
                filter_dict['is_superuser'] = str(False)
        userlist = list(UserProfile.objects.filter(**filter_dict).values())
        return JsonResponse({'status': 200, 'items': userlist, 'all_userlist': all_userlist,'total': len(userlist)})


class KubensPermise(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        filter_dict = dict()
        user_name = request.GET.get('user_name')
        cluster_name = request.GET.get('cluster_name')
        cluster_list =[(x['k8s_ident'],x['k8s_name']) for x in KubeEnv.objects.all().values('k8s_ident','k8s_name')]
        userlist = [x['username'] for x in UserProfile.objects.all().values('username')]
        if user_name:
            filter_dict['user_name'] = user_name
        if cluster_name:
            filter_dict['k8sapi'] = cluster_name
        try:
            permise_list = list(KubePermission.objects.filter(**filter_dict).values())
            return JsonResponse({'status': 200, 'items': permise_list, 'total': len(permise_list),
                                 'cluster_list': cluster_list,'userlist': userlist})
        except Exception as e:
            return JsonResponse({'status': 500,'message': str(e)})

    def post(self,request):
        if request.META.get('CONTENT_TYPE', '') == 'application/x-www-form-urlencoded':
            request_body = request.POST
        else:
            request_body = json.loads(request.body)
        action_tag = request_body['action']
        username = request_body['user_name_id']
        clusterid = request_body['k8sapi_id']
        namespace = request_body['kube_namespace']
        kube_permis = request_body['kube_permis']
        if action_tag == 'update':
            record_id = request_body['id']
            KubePermission.objects.filter(id=record_id).update(user_name=username,k8sapi_id=clusterid,kube_namespace=namespace,kube_permis=kube_permis)
            return JsonResponse({'status': 200, 'id': record_id,'message': username + ' 权限更新成功.'})
        elif action_tag == 'create':
            try:
                record_id = KubePermission.objects.create(k8sapi_id=clusterid,user_name_id=username,kube_namespace=namespace,kube_permis=kube_permis)
                record_id.save()
                return JsonResponse({'status': 200, 'id': record_id.id, 'message': username + ' 权限创建成功.'})
            except Exception as e:
                return JsonResponse({'status': 500, 'message': str(e)})
        elif action_tag == 'delete':
            record_id = request_body['id']
            KubePermission.objects.filter(id=record_id).delete()
            return JsonResponse({'status': 200, 'id': record_id,'message': username + ' 权限删除成功.'})
        else:
            return JsonResponse({'status': 403})
