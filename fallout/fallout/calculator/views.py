
import json
import requests
import re
import datetime
import time
import copy

from django.http import QueryDict, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.views.generic import View
from django.forms.formsets import formset_factory, TOTAL_FORM_COUNT
from django.core.exceptions import ValidationError
from django.utils import timezone

from .constants import SUMMARY_REPORT, SESSION_FORM_KEY, SUMMARY_REPORT_ASP_TIMEOUT, EXECUTE_STATE_COMPLETED, EXECUTE_STATE_FAILED, EXECUTE_STATE_IN_QUEUE, EXECUTE_STATE_EXECUTING
from .forms import PersonalInformation, LocationForm, BaseLocationFormSet, StateCountyForm
from .models import State, County, ExecutionTask
from .tasks import execute_report, set_false_server_response

LocationFormSet = formset_factory(LocationForm, formset=BaseLocationFormSet, can_delete=True)

def save_input_parameters(request):
    if request.method == 'POST':
        postData = handle_deleted_forms(request.POST, prefix='location_')
        locaton_formset = LocationFormSet(postData, request.FILES, prefix='location_')
        request.session[SESSION_FORM_KEY] = postData

def clear_session_parameters(request):
    if request.session.get(SESSION_FORM_KEY, None): del request.session[SESSION_FORM_KEY]
    
def inputs(request):
    postData = request.session.get(SESSION_FORM_KEY, default=None)
    form = PersonalInformation(postData)
    location_formset = LocationFormSet(postData, prefix='location_')
    location_formset.is_valid() # to trigger formset validation
    return render(request, 'inputs.html', {'form': form,
                                           'location_formset': location_formset,
                                           'version': settings.FALLOUT_VERSION,
                                           'min_dob': settings.MINIMUM_DOB,
                                           'max_dob': settings.MAXIMUM_DOB,
                                           'default_dob': settings.DEFAULT_DOB,
                                           })    
  
def clear(request):
    clear_session_parameters(request)
    return HttpResponseRedirect(reverse('inputs'))

def get_started(request):
    clear_session_parameters(request)
    return HttpResponseRedirect(reverse('inputs'))

def select_county(request):
    id_state = request.GET.get('id_state')
    id_county = request.GET.get('id_county')
    state = request.GET.get('state', '')
    county = request.GET.get('county', '').replace('%20', ' ')
    initial = {}
    if state: initial['state'] = state   
    if county: initial['county'] = county.rstrip('1234567890')
    form = StateCountyForm(initial=initial)
    return render(request, 'select_county.html', {'form':form, 'id_state': id_state, 'id_county': id_county, 
                                                  'state': state, 'county': county.rstrip('1234567890'), 'county_option': county.rstrip('1234567890').replace('_', ' ')})      

def get_counties(request):
    state = request.GET.get('state', None)
    counties = County.objects.filter(state__abbreviation=state) if state else []
    county_select = [{'value':'', 'label' : '---', 'has_map': False}] +  [{'value':c.name, 'label' : c.name, 'has_map': c.has_map} for c in counties]
    return JsonResponse(county_select, safe=False)

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
    
def test_forms_valid(request):
    postData = request.session.get(SESSION_FORM_KEY, None)        
    if postData is None: # first check if session key exists, if not, redirect to inputs page
        return False
    try:
        personal = PersonalInformation(postData)
        #LocationFormSet = formset_factory(LocationForm)
        location_formset = LocationFormSet(postData, request.FILES, prefix='location_')
        if not all([personal.is_valid(), location_formset.is_valid()]):
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
                num_locations=request.session[SESSION_FORM_KEY]['location_-TOTAL_FORMS'],
                mother_milk=request.session[SESSION_FORM_KEY]['mothers_milk_toggle'],
                thyroid_cancer=request.session[SESSION_FORM_KEY]['diagnosed_cancer'],
                fallout_version=settings.FALLOUT_VERSION,
                ade_version=settings.ADE_VERSION,
            )
            if settings.WINDOWS_SERVER == getattr(settings, 'FALSE_WINDOWS_SERVER', None):
                set_false_server_response(execution_task)
            else:
                execute_report.apply_async((execution_task.id,))
            return JsonResponse(data={'is_valid': True, 'execution_task_id': execution_task.id}, status=200)
        else:    
            return JsonResponse(data={'is_valid': False}, status=200)
    except Exception as ex:
        print(str(ex))
        return JsonResponse(data={'is_valid': False}, status=200)

def poll_execution(request):
    '''Polls execution state of the report.'''
    try:
        execution_task = get_object_or_404(ExecutionTask, pk=request.GET.get('execution_task_id', None))
        return JsonResponse(data={'completed': execution_task.state.id in (EXECUTE_STATE_COMPLETED, EXECUTE_STATE_FAILED,)}, status=200)
    except:
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
        return HttpResponseRedirect(reverse('inputs'))
    # Copy the form data to display on results page.
    form_data = copy.deepcopy(execution_task.form_data)
    
    if settings.CLEAR_RECORD_ON_RENDER:
        # Clear results and analysis form data from database record.    
        execution_task.form_data = {}
        execution_task.response_content = {}
        execution_task.save()
    
    total_time = execution_task.end_time - execution_task.create_time
    return render(request, 'results.html',
                         {'response_data': response_data,
                          'display_results': execution_task.response_code in (200, 201),
                          'version': settings.FALLOUT_VERSION,
                          'ade_version': settings.ADE_VERSION,
                          'debug': settings.DEBUG,
                          'display_raw': settings.DISPLAY_RAW_RESULTS,
                          'completed_time': execution_task.end_time,
                          'total_time': divmod(total_time.days * 86400 + total_time.seconds, 60) if settings.DEBUG else None,
                          'personal': PersonalInformation(form_data),
                          'locations': LocationFormSet(form_data, prefix='location_'),
                         })

def server_error(request, template_name='500.html'):
    return render(request, template_name, {'contact_email': settings.MANAGERS[0][1], })

class TestRunView(View):

    def get_session_parameters(self, request):
        kw = {'bda': 1, 'bmo': 11, 'byr': 1971, 'gender': 'Male', 
              'hours_outdoors': '0', 'Mothers_milk_toggle': 'Not Sure', 'diag_year': 2040,
              'location_-TOTAL_FORMS': 1,
              'location_-0-month': 11, 
              'location_-0-year': 1971, 
              'location_-0-state': 'NY', 
              'location_-0-county': 'Ulster', 
              'location_-0-milksource': 'Store Bought Cow Milk', 
              'location_-0-milkamount': 'Average', 
              'randomseed': 99,
              'sample_size': 100,
              'web_flag': 1
              
        }
        #kw.update(request.session.get(SESSION_FORM_KEY, {}))
        kw['fallout_version'] = settings.FALLOUT_VERSION
        kw['ade_version'] = settings.ADE_VERSION
        kw['summary_rpt_timeout'] = SUMMARY_REPORT_ASP_TIMEOUT
        return kw

    def get(self, request):
        start = datetime.datetime.now()
    
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, SUMMARY_REPORT), data=self.get_session_parameters(request), headers={'user-agent':'Django App (%s)' % settings.BASE_URL})
        if r.status_code != 200:
            response_data = {'messages': ['Unable to complete operation (%d).' % r.status_code]}
        else:
            response_data = r.json()
        end = datetime.datetime.now()
        total_time = end - start    
        return render(request, 'test.html',
                      {'response_data': response_data,
                       'version': settings.FALLOUT_VERSION,
                       'ade_version': settings.ADE_VERSION,
                       'debug': settings.DEBUG,
                       'total_time': divmod(total_time.days * 86400 + total_time.seconds, 60) if settings.DEBUG else None,
                      })        
