import request from '@/utils/request'

export function updateuserinfo(data) {
  return request({
    url: '/user/userinfo/',
    method: 'post',
    data
  })
}

export function getuserlist(params) {
  return request({
    url: '/user/userlist/',
    method: 'get',
    params
  })
}

export function getuserpermission(params) {
  return request({
    url: '/user/userpermission/',
    method: 'get',
    params
  })
}

export function updateuserpermission(data) {
  return request({
    url: '/user/userpermission/',
    method: 'post',
    data
  })
}
