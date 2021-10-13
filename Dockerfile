FROM python:3.6
COPY . /unicode_ops/
WORKDIR /unicode_ops
RUN pip3 install  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r /unicode_ops/requirements.txt \
&& cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# Installing OS Dependencies
RUN sed -i 's/[a-z]\{3,\}.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
&& apt-get update && apt-get upgrade -y \
&& apt-get install -y libsqlite3-dev python3-pip libsasl2-dev python3-dev libldap2-dev libssl-dev nginx \
&& pip3 install  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r /unicode_ops/requirements.txt \
&& pip3 install -U pip  --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
ENTRYPOINT [ "/bin/bash", "-x", "/unicode_ops/start.sh" ]
