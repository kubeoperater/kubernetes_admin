import os
import time
# LOGGING settings
APPENV = os.environ.get('APPENV', default='beta')
APPENV = 'local'
if APPENV == 'local':
    LOG_DIRROOT = '/Users/lei.dong/logs/'
else:
    LOG_DIRROOT = '/export/log/kubernetes-manager/'

if "HOSTNAME" in os.environ:
    LOG_DIR = LOG_DIRROOT + os.environ.get('HOSTNAME')
else:
    LOG_DIR = LOG_DIRROOT + "UNKOWN"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s FuncName:%(funcName)s LINE:%(lineno)d [%(levelname)s]- %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'info.log-{}'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024*1024*50,   # 50 MB
            'backupCount': 2,
            'formatter': 'standard',
        },
        'default_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log-{}'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024*1024*50,  # 50 MB
            'backupCount': 2,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'common.log-{}'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024*1024*50,  # 50 MB
            'backupCount': 2,
            'formatter': 'standard',
        },
        'restful_api': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'api.log-{}'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024*1024*50,  # 50 MB
            'backupCount': 2,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'default_debug'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'common': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'api': {
            'handlers': ['restful_api'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}