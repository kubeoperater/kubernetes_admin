import request from '@/utils/request'

export function projectchange(data) {
  return request({
    url: '/kube/items/projectchange/',
    method: 'post',
    data
  })
}


export function projectdeploy(data) {
  return request({
    url: '/kube/items/projectdeploy/',
    method: 'post',
    data
  })
}

export function projectlist(params) {
  return request({
    url: '/kube/items/projectlist/',
    method: 'get',
    params
  })
}

export function checkharborimg(params) {
  return request({
    url: '/kube/items/harborimageinfo/',
    method: 'get',
    params
  })
}

export function projectaskinfo(params) {
  return request({
    url: '/kube/items/projectaskinfo/',
    method: 'get',
    params
  })
}
