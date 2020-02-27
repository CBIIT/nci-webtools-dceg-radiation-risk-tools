import getpass

from fabric.tasks import task
from fabric import Connection
from paramiko.ssh_exception import AuthenticationException

dev_servers = {
    '197': {
        'pythonpath': '--redacted--/pybin/irep',
        'uwsgi': 'irep_alpha.xml',
    },
    '198': {
        'pythonpath': '--redacted--/pybin/irep',
        'uwsgi': 'irep_beta.xml',
    },
}
prod_server = {
    'pythonpath': '--redacted--/pybin/irep',
    'uwsgi': 'irep_production.xml',
}
git_path = '/usr/local/git/bin/git'

def _authenticate(connection):
    if connection.user == getpass.getuser():
        return True
    
    # TODO -- test if already authenticated
    if getattr(connection, '_is_authenticated', False):
        return True
    
    try:
        connection.connect_kwargs.password = getpass.getpass('Enter password for user {} for {}: '.format(connection.user, connection.host))
        connection.open()
        connection._is_authenticated = True
        return True
    except AuthenticationException:
        print("Authentication Failed")
        return False


def _connection_auth(src, dst):
    # copy password from passed connection if user matches and password is set.
    if src.user == dst.user and src.connect_kwargs.get('password', None):
        dst.connect_kwargs.password = src.connect_kwargs.password 
        dst._is_authenticated = True
    return dst

def _get_webserver_connection(server):
    if server in dev_servers.keys():
        connection = Connection('irepsvc@web-btp-dev-02')
        connection.pysetting = dev_servers[server]
    elif server == 'prod':
        connection = Connection('irep_dmz@web01')
        connection.pysetting = prod_server
    else:
        raise Exception('Unknown Server: {}'.format(server))
    return connection


@task
def deploy(connection, server, branch=None):
    conn = _get_webserver_connection(server)
    if _authenticate(conn):
        with conn.cd(conn.pysetting.get('pythonpath')):
            if branch:
                conn.run('git fetch origin')
                conn.run('git checkout %s' % branch)
                conn.run('git merge --ff-only origin/{}'.format(branch))
            else:
                conn.run('git pull')
            conn.run('../venv/irep/bin/pip install -Ur requirements.txt')
            conn.run('../venv/irep/bin/python manage.py migrate')
            conn.run('../venv/irep/bin/python manage.py collectstatic --noinput')
            conn.run('touch {}/uwsgi/{}'.format(conn.pysetting.get('pythonpath'), conn.pysetting.get('uwsgi')))
        
        # restart celery process
        celery(conn, server, action='restart')


@task
def celery(connection, server, action='restart'):
    assert action in ('status', 'start', 'stop', 'restart',)
    
    if server in dev_servers.keys():
        celery_conn = Connection('irepsvc@celery-btp-dev')
        celery_conn.pysetting = {
            'celeryservicerun':  'sudo /sbin/service celery-www{}-irep {}'.format(server, action)
        }
    elif server == 'prod':
        celery_conn = Connection('irep_dmz@celery-dmzst')
        celery_conn.pysetting = {
            'celeryservicerun':  'sudo /sbin/service celery-irep {}'.format(action)
        }
    else:
        raise Exception('Unknown Server: {}'.format(server))

    celery_conn = _connection_auth(connection, celery_conn)
    if _authenticate(celery_conn):
        celery_conn.config.sudo.user = 'root'
        celery_conn.run(celery_conn.pysetting.get('celeryservicerun'))

