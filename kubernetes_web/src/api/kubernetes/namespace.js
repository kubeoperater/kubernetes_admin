import request from '@/utils/request'

export function getnamespace(params) {
  return request({
    url: '/kube/ns/getinfo/',
    method: 'get',
    params
  })
}
