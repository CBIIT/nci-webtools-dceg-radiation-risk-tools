

import requests
import json
import datetime
import logging

from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from radrat.celery import app
from celery.schedules import crontab

from .models import ExecutionTask, ExecutionState
from .constants import EXECUTE_STATE_EXECUTING, EXECUTE_STATE_COMPLETED, EXECUTE_STATE_FAILED, SUMMARY_REPORT, SESSION_FORM_KEY, SUMMARY_REPORT_ASP_TIMEOUT

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_session_parameters(request):
    kw = {}
    kw.update(request.session.get(SESSION_FORM_KEY, {}))
    kw.update({'radrat_version': settings.RADRAT_VERSION, 'ade_version': settings.ADE_VERSION,})
    return kw

def get_report_data(execution_task):
    kw = {
        'randomseed': 99, 
        'sample_size': 100, 
        'web_flag': 1, 
        'radrat_version': settings.RADRAT_VERSION, 
        'ade_version': settings.ADE_VERSION,
        'summary_rpt_timeout': SUMMARY_REPORT_ASP_TIMEOUT,
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
                                              json.dumps({'elr_organ_tab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                                                            'bflr_organ_tab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                                                            'base_se_test_row19': [1.708, 1.4123, 2.0698, 4.1515, 2.2283, 1.2628, 1.1681, 2.1192, 4.6711, 0.6558, 0, 0, 5.8023, 4.0408, 1.9727, 1.0284, 0.5664, 1.8258, 3.6161], 
                                                                            'eflr_organ_tab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                                                            'risk_tab': ['Jul  1, 2015', ' ', 'Male', '1950', 'Colon Cancer', ' ', ' ', 0.00105988897566301, 0.00196154697365324, 0.00311848218216332, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.000744744078423029, 0.00149603548703153, 0.0024305541200582, 0.0370285355215894, 0.037638713417302, 0.0382551957342319, 0.0381223005751904, 0.0391347489043335, 0.0402677826984976], 
                                                                            'base_test_row1': [0, 0, 0, 0.0299, 0, 1.4064, 0, 0, 0.0299, 0, 0, 0, 0.1197, 0.0598, 1.7356, 3.5908, 0, 4.7878, 11.581], 
                                                                            'surv_test': [1, 0.99093, 0.99006, 5.54e-11], 'base_se_test_row1': [0, 0, 0, 0.0299, 0, 0.2051, 0, 0, 0.0299, 0, 0, 0, 0.0598, 0.0423, 0.2279, 0.3278, 0, 0.3785, 0.5887], 
                                                                            'base_test_row19': [60.509, 41.368, 88.859, 357.46, 102.99, 33.075, 28.302, 93.15, 452.54, 8.9196, 0, 0, 698.29, 338.66, 80.71, 21.937, 6.6535, 69.139, 271.2]}))
    execution_task.state = ExecutionState.objects.get(pk=EXECUTE_STATE_COMPLETED)
    execution_task.save()

@app.task(name='radrat.calculator.execute_report', queue=settings.CELERYQ)
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
