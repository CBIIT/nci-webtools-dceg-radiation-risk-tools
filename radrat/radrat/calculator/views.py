
import re
import datetime
import json
import logging
import copy
import requests

from django.http import QueryDict, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.forms.formsets import formset_factory, TOTAL_FORM_COUNT
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.shortcuts import render, get_object_or_404

from radrat.calculator.forms import (
    PersonalInformation, SmokingHistoryInformation, DoseUnitsForm, DoseExosureForm, BaseDoseExosureFormSet,
    AdvancedFeaturesForm, UploadFileForm,
)
from .constants import *
from .forms import ContactForm
from .models import ExecutionTask
from .tasks import execute_report, set_false_server_response

logger = logging.getLogger(__name__)

DoseExosureFormSet = formset_factory(DoseExosureForm, formset=BaseDoseExosureFormSet, can_delete=True)

def save_input_parameters(request):
    if request.method == 'POST':
        postData = handle_deleted_forms(request.POST, prefix='dose_')
        dose_formset = DoseExosureFormSet(postData, request.FILES, prefix='dose_')
        request.session[SESSION_FORM_KEY] = postData

def clear_session_parameters(request):
    if request.session.get(SESSION_FORM_KEY, None): del request.session[SESSION_FORM_KEY]

def get_session_parameters(request):
    kw = {}
    kw.update(request.session.get(SESSION_FORM_KEY, {}))
    kw.update({
        'radrat_version': settings.RADRAT_VERSION, 
        'ade_version': settings.ADE_VERSION,
        'summary_rpt_timeout': SUMMARY_REPORT_ASP_TIMEOUT,
    })
    return kw

def get_started(request):
    clear_session_parameters(request)
    return HttpResponseRedirect(reverse('model-inputs'))

def inputs(request):
    postData = request.session.get(SESSION_FORM_KEY, default=None)
    form = PersonalInformation(postData)
    smoking_history_form = SmokingHistoryInformation(postData)
    dose_units_form = DoseUnitsForm(postData)
    advanced_form = AdvancedFeaturesForm(postData)
    dose_formset = DoseExosureFormSet(postData, prefix='dose_')
    dose_formset.is_valid() # to trigger formset validation
    return render(request, 'model/inputs.html', {
        'form': form,
        'smoking_history_form': smoking_history_form,
        'dose_units_form': dose_units_form,
        'dose_formset': dose_formset,
        'advanced_form': advanced_form,
        'version': settings.RADRAT_VERSION,
    })
       
def clear(request):
    clear_session_parameters(request)
    return HttpResponseRedirect(reverse('model-inputs'))

def update_key(queryDict, key, value):
    postData = queryDict.lists()
    returnPost = QueryDict(query_string='', mutable=True)
    for (k, v,) in postData:
        if k == key:
            returnPost.setlist(k, value)
        else:
            returnPost.setlist(k, v)
    return returnPost

def handle_deleted_forms(queryDict, prefix):
    '''Since we are not actually storing forms in database, we'll need to handle removing deleted forms
       from post data manually; as well as updating formset index gaps introduced by deleted forms.
    '''

    delete_indexed = [] # all form indexes that are deleted
    (total_key, total_forms) = ('?', 1)
    for (k, v,) in queryDict.lists():
        if k.find('%s-TOTAL_FORMS' % prefix) > -1:
            (total_key, total_forms) = (k, int(v[0]))
            continue;
        m = re.match(r'%s(-\d+-)DELETE' % prefix, k)
        if m and v[0] == 'on':
            delete_indexed.append(m.group(1))

    # return passed list if no forms were deleted
    if not delete_indexed: return queryDict

    set_keys = {}
    for i in range(0, total_forms): set_keys[i] = {}

    # now delete post data for deleted forms and reset formset indexes
    returnPost = QueryDict(query_string='', mutable=True)
    for (k, v,) in sorted(queryDict.lists()):
        found = False
        for index in delete_indexed:
            found = k.find('%s%s' % (prefix, index,)) > -1
            if found: break
        if not found:
            m = re.match(r'%s-(\d+)-\w+' % prefix, k)
            if m:
                formindex = int(m.group(1))
                set_keys[formindex].update({k:v})
            else: returnPost.setlist(k, v)

    curr_formindex = 0
    for (formindex, form_list,) in sorted(set_keys.items()):
        if len(list(form_list.items())):
            for (k, v,) in list(form_list.items()):
                returnPost.setlist(k.replace('-%s-' % formindex, '-%s-' % curr_formindex), v)
            curr_formindex += 1
    returnPost.setlist(total_key, [total_forms - len(delete_indexed)])

    return returnPost

def add_formset_empty_form(dict, form, prefix):
    for name, field in list(form.base_fields.items()):
        dict['%s-__prefix__-%s' % (prefix, name,)] = field.initial
    dict['%s-__prefix__-DELETE' % prefix] = None
    return dict

def upload_template(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                files = {'template_radrat.xls': request.FILES['file']}
                r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UPLOAD_TEMPLATE), files=files, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
                if r.status_code != 200:
                    return render(request, 'model/savedfile.html', {'form': form, 'error_message': 'Unable to complete operation (%d).' % r.status_code, })
                r.raise_for_status()
                response_data = r.json()
                if response_data['error']: # detect error message and redisplay if necessary
                    return render(request, 'model/savedfile.html', {'form': form, 'error_message':str(response_data['error']['message']), })
                # detect possibly incorrect file uploaded: The asp code that reads records will fail silently, so we'll detect that failure by the total form counts being set to null.
                if response_data['dose_exposure']['%s-%s' % ('dose_', TOTAL_FORM_COUNT,)] is None: 
                    return render(request, 'model/savedfile.html', {'form': form, 'error_message':'The uploaded file does not appear to be in the expected format. Please check file or download a new template.', })
                clear_session_parameters(request)
                form_keys = response_data['personal']
                form_keys.update(response_data['smoking_history'])
                form_keys.update(response_data['dose_units'])
                form_keys.update(response_data['advanced'])
                form_keys.update(add_formset_empty_form(response_data['dose_exposure'], DoseExosureForm, 'dose_'))
                request.session[SESSION_FORM_KEY] = form_keys
            except requests.exceptions.HTTPError as e:
                return render(request, 'model/savedfile.html', {'form': form, 'error_message':str(e), })
            return HttpResponseRedirect(reverse('model-inputs'))
    else:
        form = UploadFileForm()
    return render(request, 'model/savedfile.html', {'form': form, })

def test_forms_valid(request):
    postData = request.session.get(SESSION_FORM_KEY, None)        
    if postData is None: # first check if session key exists, if not, redirect to inputs page
        return False
    try:
        personal = PersonalInformation(postData)
        smoking_history = SmokingHistoryInformation(postData)
        dose_units = DoseUnitsForm(postData)
        advanced = AdvancedFeaturesForm(postData)
        # DoseExosureFormSet = formset_factory(DoseExosureForm)
        dose_formset = DoseExosureFormSet(postData, request.FILES, prefix='dose_')
        if not all([personal.is_valid(), smoking_history.is_valid(), dose_units.is_valid(), advanced.is_valid(), dose_formset.is_valid()]):
            return False
    except ValidationError:
        return False
    else:
        return True  

def queue_report(request):
    '''Checks that report definition in post is valid. If valid, added report to execution queue. Returns whether definition is valid.'''
    try:
        # save input parameters to session.
        save_input_parameters(request)
        valid_analysis = test_forms_valid(request)
        if valid_analysis:
            execution_task = ExecutionTask.objects.create(
                form_data=request.session[SESSION_FORM_KEY], 
                num_doses=request.session[SESSION_FORM_KEY]['dose_-TOTAL_FORMS'],
                radrat_version=settings.RADRAT_VERSION,
                ade_version=settings.ADE_VERSION,
            )
            if getattr(settings, 'FALSE_WINDOWS_SERVER', False):
                set_false_server_response(execution_task)
            else:                    
                execute_report.apply_async((execution_task.id,))
            return JsonResponse(data={'is_valid': True, 'execution_task_id': execution_task.id}, status=200)
        else:    
            return JsonResponse(data={'is_valid': False}, status=200)
    except Exception as ex:
        logger.error('queue_report failed with error: {}'.format(str(ex)))
        return JsonResponse(data={'is_valid': False}, status=200)


def poll_execution(request):
    '''Polls execution state of the report.'''
    try:
        execution_task = get_object_or_404(ExecutionTask, pk=request.GET.get('execution_task_id', None))
        return JsonResponse(data={'completed': execution_task.state.id in (EXECUTE_STATE_COMPLETED, EXECUTE_STATE_FAILED,)}, status=200)
    except Exception as ex:
        logger.error('poll_execution failed with error: {}'.format(str(ex)))
        return JsonResponse(data={'completed': True}, status=200)


def summary_report(request):
    '''Renders report results.'''
    execution_task = get_object_or_404(ExecutionTask, pk=request.GET.get('execution_task_id', None))
    # Get the analysis results
    if execution_task.state.id == EXECUTE_STATE_FAILED:
        response_data = {'messages': ['Unable to complete analysis.']}
    elif execution_task.state.id in (EXECUTE_STATE_IN_QUEUE, EXECUTE_STATE_EXECUTING,):
        raise Http404("Analysis is not completed and cannot be viewed yet.")
    else:
        response_data = json.loads(execution_task.response_content)
    # If this report was viewed already, we've cleared the form data and results already -- so redirect to inputs page.  
    if not response_data:
        return HttpResponseRedirect(reverse('model-inputs'))
    # Copy the form data to display on results page.
    form_data = copy.deepcopy(execution_task.form_data)
    
    if settings.CLEAR_RECORD_ON_RENDER:
        # Clear results and analysis form data from database record.    
        execution_task.form_data = {}
        execution_task.response_content = {}
        execution_task.save()
    
    total_time = execution_task.end_time - execution_task.create_time
    return render(request, 'model/summary_report.html', {
        'response_data': response_data,
        'version': settings.RADRAT_VERSION,
        'ade_version': settings.ADE_VERSION,
        'debug': settings.DEBUG,
        'completed_time': execution_task.end_time,
        'total_time': divmod(total_time.days * 86400 + total_time.seconds, 60) if settings.DEBUG else None,        
        'personal': PersonalInformation(request.session.get(SESSION_FORM_KEY, {})),
        'smoking_history': SmokingHistoryInformation(request.session.get(SESSION_FORM_KEY, {})),
        'dose_units': DoseUnitsForm(request.session.get(SESSION_FORM_KEY, {})),
        'advanced': AdvancedFeaturesForm(request.session.get(SESSION_FORM_KEY, {})),
        'dose_exposure': DoseExosureFormSet(request.session.get(SESSION_FORM_KEY, {}), prefix='dose_'),
    })

def contact(request):
    user_message = None
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            send_mail(subject, message, sender, (settings.MANAGERS[0][1],))
            user_message = 'Thank you. We will respond as soon as possible.'
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, 'manager_email': settings.MANAGERS[0][1], 'user_message' : user_message })

def server_error(request, template_name='500.html'):
    return render(request, template_name, {'contact_email': settings.MANAGERS[0][1], })
