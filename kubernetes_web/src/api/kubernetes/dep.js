import request from '@/utils/request'

export function getdep(params) {
  return request({
    url: '/kube/dep/getinfo/',
    method: 'get',
    params
  })
}
export function changedep(data) {
  return request({
    url: '/kube/dep/change/',
    method: 'post',
    data
  })
}

