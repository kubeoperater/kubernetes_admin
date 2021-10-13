#!/usr/bin/env bash
envtag=$1
cd kubernetes_web/ && npm run build:${envtag}
[[ ${envtag} == 'beta' ]] && harbor_img="hub-dev.fengjr.com/apps/kubernetes_admin:`date +%Y%m%d%H%M%S`"
[[ ${envtag} == 'prod' ]] && harbor_img="harbor-pro.fengjr.com/ops/kubernetes-mng:`date +%Y%m%d%H%M%S`"
[[ ! -z ${harbor_img} ]] && cd ../ && docker build -t ${harbor_img} . && docker push ${harbor_img}