from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['--redacted--',]

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

WINDOWS_SERVER = '--redacted--'

# URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = '/static/fallout/'

# The absolute path to the directory where collectstatic will collect static files for deployment.
# https://docs.djangoproject.com/en/1.7/ref/settings/#static-root
STATIC_ROOT = '--redacted--/htdocs/static/fallout/'

# This setting defines the additional locations the staticfiles app will traverse if the FileSystemFinder
# finder is enabled, e.g. if you use the collectstatic or findstatic management command or use the static
#  file serving view. https://docs.djangoproject.com/en/1.7/ref/settings/#staticfiles-dirs
STATICFILES_DIRS = (
    '--redacted--/pybin/fallout/fallout/static',
)

ALLOWED_HOSTS = ['*',]

ADMINS = (
    ('Your Name', 'you@company.com'),
)

MANAGERS = ADMINS

DISPLAY_RAW_RESULTS = True

# Celery settings
CELERY_BROKER_URL = 'amqp://reb:<secret>@--redacted--/reb_vhost' # 
CELERY_BROKER_USE_SSL = True

# each site's celery worker needs its own queue
CELERYQ = 'Q197FALLOUT'

CLEAR_RECORD_ON_RENDER = False