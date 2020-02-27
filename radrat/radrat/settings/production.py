from .settings import *

DEBUG = False

PRODUCTION = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '--redacted--', 
        'USER': '--redacted--',
        'PASSWORD': '',
        'HOST': '--redacted--', 
        'PORT': '--redacted--', 
    },
}

ADMINS = (
    ('IREP Administrator', '--redacted--'),
)
MANAGERS = ADMINS

WINDOWS_SERVER = '--redacted--'

ALLOWED_HOSTS = ['*',]

# URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = '/static/radrat/'

# The absolute path to the directory where collectstatic will collect static files for deployment.
# https://docs.djangoproject.com/en/1.11/ref/settings/#static-root
STATIC_ROOT = '--redacted--/htdocs/static/radrat/'

# This setting defines the additional locations the staticfiles app will traverse if the FileSystemFinder
# finder is enabled, e.g. if you use the collectstatic or findstatic management command or use the static
#  file serving view. https://docs.djangoproject.com/en/1.11/ref/settings/#staticfiles-dirs
STATICFILES_DIRS = (
    '--redacted--/pybin/radrat/static',
)

INCLUDE_WEB_ANALYTICS = True

# Celery settings
CELERY_BROKER_URL = 'amqp://radrat:<secret>@--redacted--/radrat_vhost'
CELERY_BROKER_USE_SSL = True

# each site's celery worker needs its own queue
CELERYQ = 'QRADRAT'