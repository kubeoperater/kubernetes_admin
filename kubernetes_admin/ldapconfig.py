# https://github.com/django-auth-ldap/django-auth-ldap


import ldap
from django_auth_ldap.config import LDAPSearch,GroupOfNamesType

import logging
logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


AUTHENTICATION_BACKENDS = (
      'django_auth_ldap.backend.LDAPBackend',
      'django.contrib.auth.backends.ModelBackend',
)

BASE_DN = 'OU=unicode.vip,DC=unicode,DC=inc'
AUTH_LDAP_SERVER_URI = 'ldap://127.0.0.1'
AUTH_LDAP_BIND_DN = 'CN=ops_k8smng,OU=ops,OU=Special Account,OU=BJ,OU=unicode,DC=unicode,DC=inc'
AUTH_LDAP_BIND_PASSWORD = 'w6T3kM33'
AUTH_LDAP_USER_SEARCH = LDAPSearch(base_dn=BASE_DN, scope=ldap.SCOPE_SUBTREE, filterstr='(sAMAccountName=%(user)s)')

AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
    # 'is_active': 'userAccountControl', #userAccountControl: 512-启用,514 禁用
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 30
#ldap_group
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch(base_dn=BASE_DN, scope=ldap.SCOPE_SUBTREE,filterstr='(objectClass=groupOfNames)')
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
# # AUTH_LDAP_REQUIRE_GROUP = BASE_DN
# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     'is_active': 'cn=active,OU=凤凰金融,DC=unicode,DC=inc',
#     'is_staff': 'cn=staff,OU=凤凰金融,DC=unicode,DC=inc',
#     'is_superuser': 'cn=superuser,OU=凤凰金融,DC=unicode,DC=inc',
# }
# #如果ldap服务器是Windows的AD，需要配置上如下选项
# AUTH_LDAP_CONNECTION_OPTIONS = {
#     ldap.OPT_DEBUG_LEVEL: 1,
#     ldap.OPT_REFERRALS: 0,
# }
#
# AUTH_LDAP_FIND_GROUP_PERMS = True