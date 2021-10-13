import request from '@/utils/request'

export function getsvc(params) {
  return request({
    url: '/kube/svc/getinfo/',
    method: 'get',
    params
  })
}
