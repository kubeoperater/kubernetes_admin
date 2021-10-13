FROM node:8.9-alpine
COPY . /kubernetes_web
WORKDIR /kubernetes_web
# Installing OS Dependencies
RUN npm install --registry=https://registry.npm.taobao.org \
  && npm rebuild node-sass --registry=https://registry.npm.taobao.org
EXPOSE 9528
ENTRYPOINT [ "/bin/sh", "/kubernetes_web/start.sh" ]
