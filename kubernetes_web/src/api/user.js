import request from '@/utils/request'

export function userlogin(data) {
  return request({
    url: '/user/login/',
    method: 'post',
    data
  })
}

export function getInfo(user) {
  return request({
    url: '/user/userinfo/',
    method: 'get',
    params: { user }
  })
}

export function logout() {
  return request({
    url: '/user/logout/',
    method: 'post'
  })
}
