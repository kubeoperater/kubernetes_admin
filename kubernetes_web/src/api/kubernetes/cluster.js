import request from '@/utils/request'

export function getcluster(params) {
  return request({
    url: '/kube/cluster/getinfo/',
    method: 'get',
    params
  })
}

export function changecluster(data) {
  return request({
    url: '/kube/cluster/change/',
    method: 'post',
    data
  })
}
