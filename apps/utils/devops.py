from utils.harborapi import HarborApi
import json
import os
from django.conf import settings
HARBORUSER = os.environ.get('HARBORUSER')
HARBORPASS = os.environ.get('HARBORPASS')
HARBORHOST = os.environ.get('HARBORHOST')
harbor_client = HarborApi(HARBORHOST, HARBORUSER, HARBORPASS)

harbor_client.login_get_session_id()
status, result = harbor_client.tags_info('user/charm-web', '2019112018421911')

if 'code' in json.loads(result.decode()):
    print(json.loads(result.decode())['message'])
else:
    print(json.loads(result.decode())['name'])

# print(status,result)
# if
#     print(json.loads(result.decode())['name'])
# else:
#     print('error')
#     print(json.loads(result.decode())['message'])
