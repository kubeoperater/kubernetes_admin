# 配置邮箱发邮件的相关功能

#这一项是固定的
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# smtp服务的邮箱服务器 我用的是163
EMAIL_HOST = 'smtp.126.com'
# smtp服务固定的端口是25
EMAIL_PORT = 25
#发送邮件的邮箱
EMAIL_HOST_USER = ''
#在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = ''
#收件人看到的发件人 <此处要和发送邮件的邮箱相同>
EMAIL_FROM = ''