import json
import urllib3
import requests
import re

urllib3.disable_warnings()


class HarborApi(object):
    def __init__(self, url, username, passwd, protocol="https"):

        """
        init the request
        :param url: url address or doma
        :param username:
        :param passwd:
        :param protect:
        """
        self.url = url
        self.username = username
        self.passwd = passwd
        self.protocol = protocol

    def login_get_session_id(self):
        '''
        by the login api to get the session of id
        :return:

        '''
        harbor_version_url = "%s://%s/api/systeminfo"%(self.protocol, self.url)
        header_dict = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data_dict = {
            "principal": self.username,
            "password": self.passwd
        }
        v_req_handle = requests.get(harbor_version_url, verify=False)
        self.harbor_version = v_req_handle.json()["harbor_version"]
        if self.harbor_version.startswith("v1.4"):
            req_url = "%s://%s/login" % (self.protocol, self.url)
            self.session_id_key = 'beegosessionID'
        elif self.harbor_version.startswith("v1.8"):
            req_url = "%s://%s/c/login" % (self.protocol, self.url)
            self.session_id_key = "sid"
        elif self.harbor_version.startswith("v1.3"):
            req_url = "%s://%s/login" % (self.protocol, self.url)
            self.session_id_key = 'beegosessionID'
        else:
            raise ConnectionError("the %s version is not to supply!"%self.harbor_version)
        req_handle = requests.post(req_url, data=data_dict, headers=header_dict, verify=False)
        if 200 == req_handle.status_code:
            self.session_id = req_handle.cookies.get(self.session_id_key)
            return self.session_id
        else:
            raise Exception("login error,please check your account info!"+ self.harbor_version)


    def logout(self):
        requests.get('%s://%s/logout' %(self.protocol, self.url),
                     cookies={self.session_id_key: self.session_id})
        raise Exception("successfully logout")

    def project_info(self):
        project_url = "%s://%s/api/projects" %(self.protocol, self.url)
        req_handle = requests.get(project_url, cookies={self.session_id_key: self.session_id}, verify=False)
        if 200 == req_handle.status_code:
            return req_handle.json()
        else:
            raise Exception("Failed to get the project info。")

    def repository_info(self, project_id):
        repository_url = '%s://%s/api/repositories?project_id=%s' %(self.protocol, self.url, project_id)
        req_handle = requests.get(repository_url, cookies={self.session_id_key: self.session_id}, verify=False)
        if 200 == req_handle.status_code:
            return req_handle.json()
        else:
            raise Exception("Failed to get the repository info。")

    def tags_list(self, repository_name):
        tags_url = '%s://%s/api/repositories/%s/tags' %(self.protocol, self.url, repository_name)
        req_handle = requests.get(tags_url, cookies={self.session_id_key: self.session_id}, verify=False)
        if 200 == req_handle.status_code:
            return req_handle.json()
        else:
            raise Exception("Failed to get the tags info。")

    def tags_info(self, repository_name, tagname):
        tags_url = '%s://%s/api/repositories/%s/tags/%s' % (self.protocol, self.url, repository_name,tagname)
        req_handle = requests.get(tags_url, cookies={self.session_id_key: self.session_id}, verify=False)
        if self.harbor_version.startswith("v1.3"):
            if re.compile(r'not\s*found').findall(req_handle.content.decode()):
                message = {"code": 404, "message": req_handle.content}
            else:
                message = {"message": req_handle.content}
        else:
            message = req_handle.content
        return req_handle.status_code, message
