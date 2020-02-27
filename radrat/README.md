Quick Start
===========

1. Create/activate a virtualenv
2. `pip install -r requirements.txt`
3. Create `radrat/settings/__init__.py` file with `from .base import *`, override settings as necessary
4. `python manage.py migrate`
5. `python manage.py loaddata execution_states`
6. `python manage.py runserver`
7. `celery -A radrat worker -l info -Q QRADRAT -P gevent` -- on Windows, in separate command window

Celery Broker Notes
===================
To run locally without a broker, you can add the following to the settings to *radrat/settings/__init__.py*:

`CELERY_TASK_ALWAYS_EAGER = True`

`CELERY_TASK_EAGER_PROPAGATES = True`

This will cause the ajax call to queue report execution to block while report executes.

`CELERYQ = 'QRADRAT'`

To user broker for local Windows, you can use redis (https://github.com/ServiceStack/redis-windows).

You also need to install additional packages:

**pip install redis**

**pip install gevent**


Now run the redis server (double click executable to launch):

**\<local-redis-path\>\redis-server.exe**

Update settings in *radrat/settings/__init__.py*:

`CELERY_BROKER_URL = 'redis://localhost:6379/0'`

`BROKER_USE_SSL = False`

`CELERY_TASK_ALWAYS_EAGER = False`

`CELERY_TASK_EAGER_PROPAGATES = False `

From command window and active virtual env:

**celery -A radrat worker -l info -Q QRADRAT -P gevent**