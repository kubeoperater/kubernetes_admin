import request from '@/utils/request'

export function getnode(params) {
  return request({
    url: '/kube/node/getinfo/',
    method: 'get',
    params
  })
}
