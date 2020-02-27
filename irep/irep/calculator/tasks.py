

import requests
import json
import datetime
import logging

from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from irep.celery import app
from celery.schedules import crontab

from .models import ExecutionTask, ExecutionState
from .constants import EXECUTE_STATE_EXECUTING, EXECUTE_STATE_COMPLETED, EXECUTE_STATE_FAILED, SUMMARY_REPORT, SESSION_FORM_KEY

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_session_parameters(request):
    kw = {}
    kw.update(request.session.get(SESSION_FORM_KEY, {}))
    kw.update({'irep_version': settings.IREP_VERSION, 'ade_version': settings.ADE_VERSION,})
    return kw

def get_report_data(execution_task):
    kw = {
        'randomseed': 99, 
        'sample_size': 100, 
        'web_flag': 1, 
        'irep_version': settings.IREP_VERSION, 
        'ade_version': settings.ADE_VERSION
    }
    kw.update(execution_task.form_data)
    return kw

def set_false_server_response(execution_task):
    # Special case for scan site -- don't submit to actual Windows server.
    if getattr(settings, 'PRODUCTION', False):
        logger.error('Execution of false windows server for production site.')
    logger.warning('Executing false server ... results are not being generated by ADE.')
    execution_task.end_time = timezone.now()
    execution_task.response_code = getattr(settings, 'FALSE_WINDOWS_SERVER_RESPONSE_CODE', 200)
    execution_task.response_content = getattr(settings, 'FALSE_WINDOWS_SERVER_RESPONSE_CONTENT', 
                                              json.dumps({'sumidx_tab': ['1st', '2.5th', '5th', '10th', '25th', '50th', '75th', '90th', '95th', '97.5th', '99th'], 
                                                          'summ_tab': ['0.000', '0.011', '0.036', '0.074', '0.172', '0.391', '0.857', '1.633', '2.350', '3.463', '5.049', '0.717'],
                                                          }))
    execution_task.state = ExecutionState.objects.get(pk=EXECUTE_STATE_COMPLETED)
    execution_task.save()


@app.task(name='irep.calculator.execute_report', queue=settings.CELERYQ)
def execute_report(execution_task_id):
    try:        
        execution_task = ExecutionTask.objects.get(pk=execution_task_id)
        execution_task.start_time = timezone.now()
        execution_task.state = ExecutionState.objects.get(pk=EXECUTE_STATE_EXECUTING)
        execution_task.save()
    
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, SUMMARY_REPORT), data=get_report_data(execution_task), headers={'user-agent':'Django App (%s)' % settings.BASE_URL})
        execution_task.end_time = timezone.now()
        execution_task.response_code = r.status_code
        execution_task.response_content = r.content.decode('utf-8')
        
        # The uncertainty report isn't used currently but a rough outline of the call is included below -- should it be wanted someday.
        #form_data = copy.deepcopy(execution_task.form_data)
        #if 'report_intermediate' in form_data:            
        #    r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UNCERTAINTY_REPORT), data=get_report_data(request), headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        #    response_data.update(r.json())
        
        execution_task.state = ExecutionState.objects.get(pk=(EXECUTE_STATE_COMPLETED if execution_task.response_code == 200 else EXECUTE_STATE_FAILED))
        execution_task.save()
        
        if execution_task.state.id == EXECUTE_STATE_FAILED:
            logger.error('Execution report failed: %s' % str(execution_task.pk))
    except Exception as ex:
        logger.error('Execution report error: %s' % str(ex))
        execution_task.end_time = timezone.now()
        execution_task.state = ExecutionState.objects.get(pk=EXECUTE_STATE_FAILED)
        execution_task.exception = str(ex)
        execution_task.save()

@app.task(name='clean_execution_tasks')
def clean_execution_tasks():
    try:
        #for execution_task in ExecutionTask.objects.filter(Q(state_id=EXECUTE_STATE_FAILED) | (Q(state_id=EXECUTE_STATE_COMPLETED) & Q(end_time__lt=(timezone.now() - datetime.timedelta(days=1))))):
        for execution_task in ExecutionTask.objects.all():
            execution_task.delete()
    except Exception as ex:
        logger.error('Execution clean error: %s' % str(ex))
