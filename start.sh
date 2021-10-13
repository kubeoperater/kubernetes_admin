#!/usr/bin/env bash
cd /unicode_ops/
rm -f /etc/nginx/conf.d/*
cp default.conf /etc/nginx/conf.d/
/bin/cp nginx.conf /etc/nginx/
service nginx start
mkdir -p /export/log/kubernetes-manager
python manage.py runserver 0.0.0.0:8000 &
celery -A kubernetes_admin worker -l debug