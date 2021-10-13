import request from '@/utils/request'

export function getstatefulset(params) {
  return request({
    url: '/kube/statefulset/getinfo/',
    method: 'get',
    params
  })
}
export function changestatefulset(data) {
  return request({
    url: '/kube/statefulset/change/',
    method: 'post',
    data
  })
}
