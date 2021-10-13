import request from '@/utils/request'

export function getpod(params) {
  return request({
    url: '/kube/pod/getinfo/',
    method: 'get',
    params
  })
}

export function getpodlog(params) {
  return request({
    url: '/kube/pod/log/',
    method: 'get',
    params
  })
}

export function getnsset(params) {
  return request({
    url: '/kube/ns/getinfo/',
    method: 'get',
    params
  })
}

export function getpodbyns(params) {
  return request({
    url: '/kube/pod/byns/',
    method: 'get',
    params
  })
}

export function getcontainerbypod(params) {
  return request({
    url: '/kube/pod/containerbypod/',
    method: 'get',
    params
  })
}
