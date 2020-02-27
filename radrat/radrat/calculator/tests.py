
import os
import unittest 
import requests
import datetime

from django.test import TestCase
from django.conf import settings
from django.http import HttpRequest, QueryDict
from django.conf import settings
from django.utils import timezone

from radrat.calculator.views import get_session_parameters, SUMMARY_REPORT, UPLOAD_TEMPLATE
from radrat.calculator.forms import PersonalInformation, SmokingHistoryInformation, DoseExosureForm, AdvancedFeaturesForm
from radrat.calculator.forms import GENDER_CHOICES, DOSETYPE_CHOICES, EXPRATE_CHOICES, ORGAN_CHOICES, BASELINE_CHOICES, LEUKEMIA_MODEL_CHOICES, THYROID_MODEL_CHOICES
from radrat.calculator.constants import *
from radrat.calculator.utils import _thread_locals

class BaseTestCase(TestCase):
    
    TEST_XLS = os.path.join(settings.BASE_DIR, '..', 'test', 'xls')

    def get_excel_template_parse(self, filename, override_year='2012'):
        '''Reads parameters from Excel file which is parsed by Windows server procedure.'''
        request = HttpRequest()
        request.session = {}                
        params = QueryDict(query_string='', mutable=True)
                            
        files = {'template_radrat.xls': open(filename, "rb")}
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UPLOAD_TEMPLATE), files=files, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()
        
        params.update(response_data['personal'])
        params.update(response_data['smoking_history'])
        params.update(response_data['advanced'])
        params.update(response_data['dose_units'])
        params.update(response_data['dose_exposure'])   
        # Override the 'year_today' field to a year where results are already known -- excel parser defaults to the current year.        
        if override_year:
            params['year_today'] = override_year
        request.session[SESSION_FORM_KEY] = params
        return get_session_parameters(request)

    def get_default_params_dict(self):
        '''Create test collection of parameters.'''
        # Create an HttpRequest -- so that we can mimic behavior in actual view function.        
        request = HttpRequest()
        request.session = {}
        postData = QueryDict(query_string='', mutable=True)
        postData.update({'gen_choice': GENDER_CHOICES[2][0], 'by': 1950, 'baseline': BASELINE_CHOICES[1][0],})
        postData.update({'include_history': '', 'cpd_intensity_inp': None, 'start_smk_yr_inp': None, 'quit_smk_p_inp': None,})
        postData.update({'dose_units': 'mGy', 'dose_-TOTAL_FORMS': 1, 'dose_-INITIAL_FORMS': 0, 'dose_-MAX_NUM_FORMS': 200, 'dose_-0-event': 1, 'dose_-0-yoe': 1980, 'dose_-0-organ': ORGAN_CHOICES[5][0], 'dose_-0-exprate': EXPRATE_CHOICES[1][0], 'dose_-0-dosetype': DOSETYPE_CHOICES[1][0], 'dose_-0-doseparm1': 100, 'dose_-0-doseparm2': 0, 'dose_-0-doseparm3': 0, })
        postData.update({'sample_size': 300, 'random_seed': 99, 'year_today': '2012', 'ududtype': DOSETYPE_CHOICES[1][0], 'ududparm1': 1, 'ududparm2': 0, 'ududparm3': 0, 'leukemia_choice': LEUKEMIA_MODEL_CHOICES[1][0], 'thyroid_choice': THYROID_MODEL_CHOICES[1][0], })
        request.session[SESSION_FORM_KEY] = postData
        return get_session_parameters(request)

class BaseFormTests(BaseTestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.session = {}
        _thread_locals.request = self.request
        
    def baseline_PersonalInformation(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'gen_choice': GENDER_CHOICES[1][0], 'by': 1950, 'baseline': BASELINE_CHOICES[1][0],})
        form = PersonalInformation(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data

    def baseline_SmokingHistory(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'include_history': '', 'cpd_intensity_inp': None, 'start_smk_yr_inp': None, 'quit_smk_p_inp': None})
        form = SmokingHistoryInformation(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data
    
    def baseline_DoseExosureForm(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'event':1, 'yoe':1980, 'exprate':EXPRATE_CHOICES[1][0], 'organ':ORGAN_CHOICES[5][0], 'dosetype':DOSETYPE_CHOICES[1][0], 'doseparm1':100, 'doseparm2':0, 'doseparm3':0, })
        form = DoseExosureForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data

    def baseline_AdvancedFeaturesForm(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'sample_size': 300, 'random_seed': 99, 'year_today': datetime.date.today().year, 'ududtype': DOSETYPE_CHOICES[1][0], 'ududparm1': 1, 'ududparm2': 0, 'ududparm3': 0, 'leukemia_choice': LEUKEMIA_MODEL_CHOICES[1][0], 'thyroid_choice': THYROID_MODEL_CHOICES[1][0], })
        form = AdvancedFeaturesForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data
    
class PersonalInformationTests(BaseFormTests):
    def setUp(self):
        super(PersonalInformationTests, self).setUp()

    def test_baseline(self):
        formData = self.baseline_PersonalInformation()
        formData.setlist('baseline', [BASELINE_CHOICES[0][0], ]) # set baseline to blank
        form = PersonalInformation(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")    

class SmokingHistoryTests(BaseFormTests):
    def setUp(self):
        super(SmokingHistoryTests, self).setUp()

    def test_baseline(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_SmokingHistory()
        form = SmokingHistoryInformation(data=formData)
        self.assertTrue(form.is_valid(), "Not expectedly form to have errors.")         
        
    def test_include_smoking_zero_cigarettes(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_SmokingHistory()        
        formData.setlist('include_history', ['on',])        
        formData.setlist('cpd_intensity_inp', [0,])        
        form = SmokingHistoryInformation(data=formData)
        self.assertTrue(form.is_valid(), "Not expectedly form to have errors.")        

    def test_include_smoking_cigarettes(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_SmokingHistory()
        formData.setlist('include_history', ['on',])
        formData.setlist('cpd_intensity_inp', [1,])
        formData.setlist('start_smk_yr_inp', [1975,])
        form = SmokingHistoryInformation(data=formData)
        self.assertTrue(form.is_valid(), "Not expectedly form to have errors.")

    def test_include_smoking_start_before_birth_year(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_SmokingHistory()
        formData.setlist('include_history', ['on',])
        formData.setlist('cpd_intensity_inp', [1,])
        formData.setlist('start_smk_yr_inp', [1945,])
        form = SmokingHistoryInformation(data=formData)
        self.assertFalse(form.is_valid(), "Expecting form to have errors.")        
        
    def test_include_smoking_end_before_start(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_SmokingHistory()
        formData.setlist('include_history', ['on',])
        formData.setlist('cpd_intensity_inp', [1,])
        formData.setlist('start_smk_yr_inp', [1975,])
        formData.setlist('quit_smk_p_inp', [1965,])
        form = SmokingHistoryInformation(data=formData)
        self.assertFalse(form.is_valid(), "Expecting form to have errors.")        
        
    def test_include_smoking_start_after_current_year(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_SmokingHistory()
        formData.setlist('include_history', ['on',])
        formData.setlist('cpd_intensity_inp', [1,])
        formData.setlist('start_smk_yr_inp', [timezone.now().year + 1,])
        form = SmokingHistoryInformation(data=formData)
        self.assertFalse(form.is_valid(), "Expecting form to have errors.")         

    def test_include_smoking_end_after_current_year(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_SmokingHistory()
        formData.setlist('include_history', ['on',])
        formData.setlist('cpd_intensity_inp', [1,])
        formData.setlist('start_smk_yr_inp', [1972,])
        formData.setlist('quit_smk_p_inp', [timezone.now().year + 1,])
        form = SmokingHistoryInformation(data=formData)
        self.assertFalse(form.is_valid(), "Expecting form to have errors.")         
        
class DoseExposureFormTests(BaseFormTests):
    def setUp(self):
        super(DoseExposureFormTests, self).setUp()

    def test_event(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        # test that yoe is required
        formData = self.baseline_DoseExosureForm()
        formData.setlist('event', []) # set event to blank
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")    

    def test_yoe(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        # test that yoe is required
        formData = self.baseline_DoseExosureForm()
        formData.setlist('yoe', []) # set yoe to blank
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")    
        # test that yoe can not be before by
        self.assertTrue(data['by'] == 1950, "Expecting birth year to equal 1950.")
        formData.setlist('yoe', [1949, ])
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")  

    def test_organ(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        # test that organ is required
        formData = self.baseline_DoseExosureForm()
        formData.setlist('organ', ORGAN_CHOICES[0][0]) # set organ to blank
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")   
         
        # test that certain organs are specific to male gender
        self.assertTrue(data['gen_choice'] == GENDER_CHOICES[1][0], "Expecting gender to be female.")
        formData.setlist('organ', ORGAN_CHOICES[14][0]) # set organ to prostate.
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")
        # test that certain organs are specific to female gender
        data['gen_choice'] = GENDER_CHOICES[2][0]
        self.request.session[SESSION_FORM_KEY] = data   
        formData.setlist('organ', ORGAN_CHOICES[11][0]) # set organ to breast.
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")
        formData.setlist('organ', ORGAN_CHOICES[12][0]) # set organ to ovary.
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")
        formData.setlist('organ', ORGAN_CHOICES[13][0]) # set organ to uterus.
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")

    def test_exprate(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        # test that exprate is required
        formData = self.baseline_DoseExosureForm()
        formData.setlist('exprate', [EXPRATE_CHOICES[0][0], ]) # set exprate to blank
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.") 

    def test_dosetype(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        # test that dosetype is required
        formData = self.baseline_DoseExosureForm()
        formData.setlist('dosetype', DOSETYPE_CHOICES[0][0]) # set dosetype to blank
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")    

class AdvancedFeaturesFormTests(BaseFormTests):
    def setUp(self):
        super(AdvancedFeaturesFormTests, self).setUp()

    def test_dose_type(self):
        formData = self.baseline_AdvancedFeaturesForm()
        formData.setlist('ududtype', [DOSETYPE_CHOICES[0][0], ]) # set dose type to blank
        form = AdvancedFeaturesForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")    

class Template_Excel_ASP_Tests(BaseTestCase):
    def assert_expected_keys(self, response_data):
        self.assertTrue('personal' in response_data, "Missing expected key 'personal'.")
        self.assertTrue('smoking_history' in response_data, "Missing expected key 'personal'.")
        self.assertTrue('dose_exposure' in response_data, "Missing expected key 'dose_exposure'.")   
        self.assertTrue('advanced' in response_data, "Missing expected key 'advanced'.")   
            
    def test_excel_template_parse(self):
        files = {'template_nih.xls': open(os.path.join(os.path.join(settings.STATIC_ROOT, 'docs', 'template_radrat.xls')), "rb")}
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UPLOAD_TEMPLATE), files=files, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()
        
        # compare parsed template with expected values
        self.assertEqual(response_data['personal'], {'by': 1950, 'gen_choice': 'Male', 'baseline': BASELINE_CHOICES[1][0], }, "'personal' does not match expected values.")
        self.assertEqual(response_data['smoking_history'], {'start_smk_yr_inp': 1970, 'quit_smk_p_inp': None, 'cpd_intensity_inp': 0, 'include_history': ''}, "'smoking_history' does not match expected values.")
        self.assertEqual(response_data['dose_exposure'],
                         {'dose_-TOTAL_FORMS': 1, 'dose_-0-doseparm1': 100, 'dose_-0-doseparm2': 0, 'dose_-0-doseparm3': 0, 'dose_-0-yoe': 1980, 'dose_-0-organ': 'Colon', 'dose_-INITIAL_FORMS': 0, 'dose_-0-dosetype': 'Fixed Value', 'dose_-0-exprate': 'a', 'dose_-0-event': 1, 'dose_-MAX_NUM_FORMS': ''},
                         "'dose_exposure' does not match expected values.")
        self.assertEqual(response_data['advanced'],
                         {'random_seed': 99, 'ududparm3': 0, 'year_today': datetime.date.today().year, 'ududparm2': 0, 'ududparm1': 1, 'sample_size': 300, 'ududtype': 'Fixed Value', 'leukemia_choice': LEUKEMIA_MODEL_CHOICES[1][0], 'thyroid_choice': THYROID_MODEL_CHOICES[1][0],},
                         "'advanced' does not match expected values.")

class Summary_Report_ASP_Tests(BaseTestCase):    
    def assert_expected_keys(self, response_data):
        self.assertTrue('risk_tab' in response_data, "Missing expected key 'risk_tab'.")
        self.assertTrue('elr_organ_tab' in response_data, "Missing expected key 'elr_organ_tab'.")
        self.assertTrue('eflr_organ_tab' in response_data, "Missing expected key 'eflr_organ_tab'.")
        self.assertTrue('bflr_organ_tab' in response_data, "Missing expected key 'bflr_organ_tab'.")

    def assert_summary_results(self, response_data, expected_messages, expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab):
        # check for expected keys
        self.assert_expected_keys(response_data)        
        # check expected values
        self.assertEqual(expected_risk_tab[1:], response_data['risk_tab'][1:], "'risk_tab' does not match expected values.\nobservered: %s\nexpected: %s" % (response_data['risk_tab'], expected_risk_tab))
        self.assertEqual(expected_elr_organ_tab, response_data['elr_organ_tab'], "'elr_organ_tab' does not match expected values.\nobserved: %s\nexpected: %s" % (response_data['elr_organ_tab'], expected_elr_organ_tab))
        self.assertEqual(expected_eflr_organ_tab, response_data['eflr_organ_tab'], "'eflr_organ_tab' does not match expected values.\nobserved: %s\nexpected: %s" % (response_data['eflr_organ_tab'], expected_eflr_organ_tab))
        self.assertEqual(expected_bflr_organ_tab, response_data['bflr_organ_tab'], "'bflr_organ_tab' does not match expected values.\nobserved: %s\nexpected: %s" % (response_data['bflr_organ_tab'], expected_bflr_organ_tab))
        self.assertEqual(expected_messages, response_data['messages'], "'messages' does not match expected values.")

    def test_summary_report_defaults(self):
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, SUMMARY_REPORT), data=self.get_default_params_dict(), headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,}, timeout=SUMMARY_REPORT_ASP_TIMEOUT)
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()        
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Male', '1950', 'Colon Cancer', ' ', ' ', 0.00105988897566301, 0.00196154697365324, 0.00311848218216332, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.000839780819107408, 0.00169111220515645, 0.00274887874650917, 0.0398546845573618, 0.0405187550995336, 0.0411897589396252, 0.0410851065996508, 0.0422098673046901, 0.0434798303268673]
        expected_elr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_eflr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_bflr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_messages = [
            "ADE Message for objName 'definition' : Attribute could not be set (code 36) (OutputBuffer: Evaluation error in Start_smk_yr_inp: \r\nDecision Start_smk_yr_inp has not been explicitly defined yet.)", 
            "ADE Message for objName 'definition' : Attribute could not be set (code 36) (OutputBuffer: Evaluation error in Quit_smk_p_inp: \r\nDecision Quit_smk_p_inp has not been explicitly defined yet.)", "ADE Message for objName 'definition' : Attribute could not be set (code 36) (OutputBuffer: Evaluation error in Cpd_intensity_inp: \r\nVariable Cpd_intensity_inp has not been explicitly defined yet.)",
        ]        
        self.assert_summary_results(response_data, expected_messages, expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    def assert_summary_results_from_template(self, template, expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, template))
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, SUMMARY_REPORT), data=params, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,}, timeout=SUMMARY_REPORT_ASP_TIMEOUT)
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()
        expected_messages = ["ADE Message for objName 'definition' : Attribute could not be set (code 36) (OutputBuffer: Evaluation error in Quit_smk_p_inp: \r\nDecision Quit_smk_p_inp has not been explicitly defined yet.)"]
        self.assert_summary_results(response_data, expected_messages, expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)
    
    def test_summary_report_example1(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Male', '1980', 'Colon Cancer', ' ', ' ', 0.000123568592062798, 0.000272888944142521, 0.000470672303704428, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.000124692255457898, 0.000274380418712879, 0.000468721848872654, 0.0412252306151074, 0.0419722150168136, 0.0427283540632229, 0.0414524144481578, 0.0422465954355265, 0.0430229460757841]
        expected_elr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_eflr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_bflr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "RC_Example1.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    def test_summary_report_example2(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Female', '1990', 'Cancer of the Exposed Organs', ' ', ' ', 0.000500236293821628, 0.00100045528420074, 0.00176611353728041, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.000479958116669844, 0.000985345260257813, 0.00176047901400283, 0.370311061384394, 0.37786927229198, 0.385580630414966, 0.371731421502811, 0.378854617552237, 0.386709537159504]
        expected_elr_organ_tab = [2.38990140048436e-08, -9.02519601916554e-08, 2.8161111858036e-05, 7.41155916714681e-05, -3.14183838084012e-06, 6.11833263797392e-06, -1.37125779552166e-05, 8.80792614538041e-06, 5.28992087905779e-05, 3.79078897740747e-05,1.99576113450263e-05, -2.81353230792985e-05, 0, 1.76755550712811e-05, 7.55609420927669e-06, 0, 5.74552589939024e-07, 1.1348625117205e-05, 0, 9.95555087028263e-08, 7.79461419855664e-07, 0.000205726354613527, 0.000181462936589045, 1.49636270340293e-05, 6.08188594117073e-05, -1.19663517830794e-06, 5.17297256643667e-05, 0.00012811279394074, 7.08748384183308e-05, 7.8768199851231e-05, 4.5016998798145e-05, 0, 5.76377564524779e-05, 5.71041520213266e-05, 0, 2.42716282716218e-06, 4.61294968284026e-05, 0, 2.33534115891359e-07, 2.3016432332312e-06, 0.000769504125014726, 0.000357359586846993, 4.36129487275224e-05, 0.000221422944693925, 9.65460712429867e-06, 0.000117637091938998, 0.00028810087043212, 0.00011867039595356, 0.000185349392467581, 0.00014784960957558, 0, 0.000121886508246762, 0.000144514656886213, 0, 6.01180522838893e-06, 0.000115066055599388, 0]
        expected_eflr_organ_tab = [2.34347198690776e-08, -9.04979352852691e-08, 2.81663918573424e-05, 7.41532319462031e-05, -3.14364954154605e-06, 6.08055623450323e-06, -1.37600653861441e-05, 8.81807580867228e-06, 5.30871298135188e-05, 3.7936244418445e-05, 1.99330167173875e-05, -2.80630026595231e-05, 0, 1.77379366546587e-05, 7.55424889378002e-06, 0, 5.61759852682155e-07, 5.69203675912675e-06, 0, 9.78775123040649e-08, 7.81156400038265e-07, 0.000205835731760818, 0.000181712915546251, 1.49758749443272e-05, 6.09098011628017e-05, -1.20056327087843e-06, 5.183988207055e-05, 0.000128523011087267, 7.09420633612078e-05, 7.76343367116594e-05, 4.50081328836718e-05, 0, 5.77376633825382e-05, 5.70309680409734e-05, 0, 2.37120640573652e-06, 3.11452022585466e-05, 0, 2.31484851371855e-07, 2.30796158250927e-06, 0.00076926449640282, 0.000358013016067181, 4.36437341202489e-05, 0.000222124466750472, 9.68706564077554e-06, 0.00011793917106475, 0.000288941326827725, 0.000118799712595786, 0.000182404796874393, 0.000147886253969223, 0, 0.000122052056005762, 0.000144414355819597, 0, 5.88735436583787e-06, 8.37631909685296e-05, 0]
        expected_bflr_organ_tab = [0.00655175220496893, 0.00232436793401967, 0.00660582942207042, 0.0417444960580897, 0.0143482234536287, 0.0032789755149775, 0.00351987184791448, 0.0127490438249613, 0.0631127913914777, 0.13193856141198, 0.0140136558724661, 0.0320646013704687, 0, 0.011646244378313, 0.0101454558759178, 0, 0.0100951251103431, 0.00617206571279723, 0, 0.00685853937106352, 0.00249548428083504, 0.0069028883026539, 0.042471367839696, 0.0147911291097336, 0.00348764789875177, 0.00373082179283637, 0.013146599784657, 0.0639965876179474, 0.133290092979418, 0.0144620722384969, 0.0327432011643348, 0, 0.0120287324118662, 0.0105191957596981, 0, 0.0104718505798481, 0.00647306116014317, 0, 0.00717492339914109, 0.00267598749430775, 0.00720952970823762, 0.0432078414109992, 0.0152436307801643, 0.00370587520364667, 0.00395124759073981, 0.0135537179582604, 0.0648899800324434, 0.134651231759378, 0.0149200915087491, 0.0334314073672839, 0, 0.0124208014576316, 0.010902528975019, 0, 0.0108581779872415, 0.00678365778172288, 0]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "RC_Example2.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    def test_summary_report_example3(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Female', '1950', 'Breast Cancer', ' ', ' ', 9.32107619363978e-06, 1.83082344721699e-05, 3.31761494464558e-05, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 7.6061269385355e-06, 1.49777314933833e-05, 2.72544330891223e-05, 0.0893655103357529, 0.090279718378007, 0.0911998594451323, 0.0893771518262775, 0.0902946961095003, 0.0912101778600372]
        expected_elr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_eflr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_bflr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "RC_Example3.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    def test_summary_report_example4(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Female', '1950', 'Breast Cancer', ' ', ' ', 0.0001004808192638, 0.000193983099706167, 0.000346040844878885, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 8.2073059846843e-05, 0.000155775088313559, 0.000277015194982645, 0.0893686634472182, 0.0902797153712899, 0.0911966408709373, 0.08951206159776, 0.0904354904596035, 0.0913761804003465]
        expected_elr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_eflr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        expected_bflr_organ_tab = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "RC_Example4.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    @unittest.skip("This report times out (504).")
    def test_summary_report_example5(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Male', '1991', 'Cancer of the Exposed Organs', ' ', ' ', 0.000959665358793316, 0.00183239158661297, 0.00329413551517689, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.000956377238372105, 0.00182625184561196, 0.00328219509306533, 0.479273057085694, 0.4880181617943, 0.496924419549382, 0.480827150897986, 0.489844413639912, 0.499021562242201]
        expected_elr_organ_tab = [3.14983217584656e-06, 1.16718532096891e-05, 1.14656550114517e-05, 0.000108811915525403, -5.0617612849223e-06, 1.44812101432614e-05, -9.71137472296994e-06, 6.11237616569439e-06, 8.02720244852458e-05, 0, 0, 0, -0.000549056871075714, 5.12575995853008e-05, 4.38977065118753e-06, 1.04812163101325e-05, 9.02219161142117e-06, 4.94285352640352e-05, 0.000108426286714134, 3.66099719016195e-05, 4.83861800414294e-05, 0.000105402908474494, 0.00025091188359373, 2.49801218154758e-05, 7.21889241233126e-05, -6.48255463598957e-07, 4.26971661177004e-05, 0.000226658300267975, 0, 0, 0, 0.000151574251514263, 0.000180312517187848, 5.91724876844019e-05, 4.44965399137708e-05, 4.30570862936768e-05, 0.000137485146427455, 0.000409106356719417, 8.38921278011437e-05, 0.000114984414453814, 0.000415969460086294, 0.00046253196433041, 7.28318911245988e-05, 0.000237080172995765, 5.78124372957403e-06, 9.51676754510522e-05, 0.000434017980063436, 0, 0, 0, 0.00101676339125364, 0.000431654401242006, 0.000163380800411566, 0.000103708206989449, 0.000118552891774795, 0.000295903063259547, 0.000867399589514583]
        expected_eflr_organ_tab = [3.13869317890775e-06, 1.16158732496447e-05, 1.14290747985076e-05, 0.000108515870351789, -5.04830924650033e-06, 1.44239364071129e-05, -9.66460858383628e-06, 6.08971596202505e-06, 7.98979822856243e-05, 0, 0, 0, -0.000546917123824933, 5.10755351670103e-05, 4.3762890423743e-06, 1.04451235431867e-05, 8.99972157290726e-06, 4.92453209113928e-05, 0.00010801023738619, 3.64888460155949e-05, 4.82227973810198e-05, 0.00010505806891158, 0.000250055441444903, 2.48965656651247e-05, 7.1949938901776e-05, -6.45792238645024e-07, 4.25512411479647e-05, 0.00022589724958711, 0, 0, 0, 0.000151035810623728, 0.00017968506119881, 5.89750645471806e-05, 4.43548458309072e-05, 4.29557556256325e-05, 0.000136963365173495, 0.000407807585795778, 8.3629645053092e-05, 0.000114610305959077, 0.000414310792469379, 0.000461060849448248, 7.26198628833328e-05, 0.000236309993505309, 5.76262680308184e-06, 9.48441780052657e-05, 0.000432547147588802, 0, 0, 0, 0.00101330554712192, 0.000429950993624673, 0.000162728547549236, 0.000103441580509595, 0.00011829672344244, 0.000294773797571486, 0.000864679842287969]
        expected_bflr_organ_tab = [0.0140177749140833, 0.00738912545853665, 0.0107466596165209, 0.0407314522090383, 0.0181731745097176, 0.00807805462061627, 0.00271135133234333, 0.0124134235601289, 0.0796573155004328, 0, 0, 0, 0.165263063577365, 0.0368186433168306, 0.0173747300585173, 0.0057683353256612, 0.00354172133954926, 0.00816065196990789, 0.0484275797764443, 0.0144660346457607, 0.0077056718510219, 0.0111376140433051, 0.0414813680357129, 0.0186824071176346, 0.00841389453960862, 0.00290391114999697, 0.0128244824856109, 0.0806727230162699, 0, 0, 0, 0.166675529980033, 0.0375174521166366, 0.0178713686203173, 0.00607051121208334, 0.00377358759841992, 0.00851844901537608, 0.0493031563665125, 0.0149244173331548, 0.00803226695589443, 0.0115386770815209, 0.0422414079924205, 0.0192017558740114, 0.00875983948452536, 0.00310612466748042, 0.013245613195773, 0.0816982497759448, 0, 0, 0, 0.168097953154918, 0.038226376524789, 0.0183781253493148, 0.00638281004879038, 0.00401556639830331, 0.00888637118831448, 0.0501888645242268]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "RC_Example5.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    def test_summary_report_user_example1(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Male', '1950', 'Cancer of the Exposed Organs', ' ', ' ', 0.00092981994015215, 0.00316439511940449, 0.00774490588870564, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.000897480338801306, 0.00325629995927496, 0.00794034736560909, 0.0728082043565741, 0.0746065579537278, 0.0764395540264877, 0.0744880659996826, 0.0778628579130028, 0.082842922780536]
        expected_elr_organ_tab = [0, 0, 5.91492610534183e-05, 0.000345212180095084, 0, 1.1369978480323e-05, 0, 0, 0, 0, 0, 0, 0, 0, 2.75062192183501e-05, 0, 2.14021164915788e-07, 0, 0, 0, 0, 0.000479359092769595, 0.00232328643348412, 0, 7.00174274612862e-05, 0, 0, 0, 0, 0, 0, 0, 0, 0.000289237536722952, 0, 2.49462896653655e-06, 0, 0, 0, 0, 0.00184368600801643, 0.00675938526177053, 0, 0.000241463494933366, 0, 0, 0, 0, 0, 0, 0, 0, 0.000759951197246182, 0, 7.30129304445581e-06, 0, 0]
        expected_eflr_organ_tab = [0, 0, 5.48555080942407e-05, 0.000370002429477784, 0, 9.74701800744135e-06, 0, 0, 0, 0, 0, 0, 0, 0, 2.5575553288119e-05, 0, 2.24249477431017e-07, 0, 0, 0, 0, 0.000441679930157458, 0.00247812028982252, 0, 6.56501548337646e-05, 0, 0, 0, 0, 0, 0, 0, 0, 0.000268242415144754, 0, 2.6071693164677e-06, 0, 0, 0, 0, 0.00169611240557793, 0.00704223584560885, 0, 0.000233692885385195, 0, 0, 0, 0, 0, 0, 0, 0, 0.000701958038872586, 0, 7.70495377012481e-06, 0, 0]
        expected_bflr_organ_tab = [0, 0, 0.0102475759110439, 0.0398546845573618, 0, 0.00621682000202202, 0, 0, 0, 0, 0, 0, 0, 0, 0.014583771669617, 0, 0.00190535221652934, 0, 0, 0, 0, 0.0105852216439478, 0.0405187550995336, 0, 0.00647588229696919, 0, 0, 0, 0, 0, 0, 0, 0, 0.0149807843495667, 0, 0.00204591456371046, 0, 0, 0, 0, 0.0109297990971797, 0.0411897589396252, 0, 0.00674187383304584, 0, 0, 0, 0, 0, 0, 0, 0, 0.0153847289377465, 0, 0.00219339321889041, 0, 0]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "user_example1.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    def test_summary_report_user_example2(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Male', '1950', 'Cancer of the Exposed Organs', ' ', ' ', 0.000371461005695457, 0.00161538462291334, 0.00392294519864618, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.000386183361090863, 0.00167927571812423, 0.00407740907600722, 0.0728082043565741, 0.0746065579537278, 0.0764395540264877, 0.0739405060445627, 0.0762858336718521, 0.0789761418424943]
        expected_elr_organ_tab = [0, 0, 1.13744989044335e-05, 8.86868952278891e-05, 0, 1.15838044722019e-05, 0, 0, 0, 0, 0, 0, 0, 0, 5.24353658352884e-06, 0, 4.8887192326325e-07, 0, 0, 0, 0, 0.00031704924560454, 0.000892517741836912, 0, 0.000238622035067882, 0, 0, 0, 0, 0, 0, 0, 0, 0.000160689236939923, 0, 6.50636346408419e-06, 0, 0, 0, 0, 0.00127946698231393, 0.00274800662284029, 0, 0.000980450537265825, 0, 0, 0, 0, 0, 0, 0, 0, 0.000576396531269851, 0, 2.18946159415e-05, 0, 0]
        expected_eflr_organ_tab = [0, 0, 1.18252184927118e-05, 9.2195876303194e-05, 0, 1.2042845370888e-05, 0, 0, 0, 0, 0, 0, 0, 0, 5.44744480031364e-06, 0, 5.08197508089148e-07, 0, 0, 0, 0, 0.000329586868238628, 0.00092783285522354, 0, 0.000248062975236197, 0, 0, 0, 0, 0, 0, 0, 0, 0.000167034387061486, 0, 6.75863236437414e-06, 0, 0, 0, 0, 0.00133016485776227, 0.00285689914286036, 0, 0.0010192585697097, 0, 0, 0, 0, 0, 0, 0, 0, 0.000599196301770771, 0, 2.27613208024508e-05, 0, 0]
        expected_bflr_organ_tab = [0, 0, 0.0102475759110439, 0.0398546845573618, 0, 0.00621682000202202, 0, 0, 0, 0, 0, 0, 0, 0, 0.014583771669617, 0, 0.00190535221652934, 0, 0, 0, 0, 0.0105852216439478, 0.0405187550995336, 0, 0.00647588229696919, 0, 0, 0, 0, 0, 0, 0, 0, 0.0149807843495667, 0, 0.00204591456371046, 0, 0, 0, 0, 0.0109297990971797, 0.0411897589396252, 0, 0.00674187383304584, 0, 0, 0, 0, 0, 0, 0, 0, 0.0153847289377465, 0, 0.00219339321889041, 0, 0]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "user_example2.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    def test_summary_report_user_example3(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Male', '1950', 'Cancer of the Exposed Organs', ' ', ' ', 0.00502709038777767, 0.0134596274653076, 0.0287820492200536, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.00521355030464176, 0.0139698237708998, 0.0299012494019265, 0.442667135793779, 0.450005341986822, 0.45745443325635, 0.451157522620465, 0.463975165757722, 0.480684157013443]
        expected_elr_organ_tab = [7.37299697977917e-06, 2.35166117535024e-05, 2.86498160486203e-05, 0.000228333995398976, -2.08534900019166e-05, 2.26386673297875e-05, -7.54124586944954e-05, 1.70311011123985e-05, 0.000165609481812397, 0, 0, 0, -0.00290562223899024, 0.000154570774178365, 1.36369728275273e-05, 1.66930128364001e-05, 9.59536209152911e-07, 0.000280945495042881, 0.000240714397637872, 0.000180194703167939, 0.000345199494381997, 0.000864816306967317, 0.00213067916668616, 0.000172754583903322, 0.000610885305223171, -2.30927961203282e-06, 0.00035793072930563, 0.00204412087813888, 0, 0, 0, 0.000750009044390773, 0.00171707680542232, 0.000376143752157554, 0.000226274718243289, 1.63294815123779e-05, 0.00134498500315417, 0.00232453677226469, 0.000645055151499988, 0.00111981002867826, 0.00398091750892724, 0.00673802264967675, 0.000596772947516012, 0.00248380387903057, 6.89877629964e-05, 0.00127587047034523, 0.0068333725218132, 0, 0, 0, 0.00858900589370897, 0.00578204332412729, 0.00146248485160695, 0.000774633579548087, 5.11760299683225e-05, 0.00342193495061551, 0.00731940416466119]
        expected_eflr_organ_tab = [7.66481674561036e-06, 2.44464677592979e-05, 2.97836032935711e-05, 0.000237371818889586, -2.16787661101584e-05, 2.35352326964876e-05, -7.83764209746702e-05, 1.77057071307403e-05, 0.000172143159799605, 0, 0, 0, -0.00301964454380554, 0.000160695933516664, 1.41702087019946e-05, 1.73530303440857e-05, 9.97542037354054e-07, 0.000285977841460111, 0.000250217012458734, 0.00018731019723259, 0.000358850859802933, 0.000899022992507382, 0.00221498265468365, 0.000179587581312119, 0.000635055396842171, -2.40060943726393e-06, 0.000372086248595053, 0.00212500613904884, 0, 0, 0, 0.000779616604333764, 0.0017850293830699, 0.000390995727697695, 0.000235217420809939, 1.69626878926308e-05, 0.00137603354615722, 0.00241646694035117, 0.000670577355597291, 0.00116410836639956, 0.00413865938254274, 0.00700501618324665, 0.000620406415599119, 0.00258223759433514, 7.17143586594413e-05, 0.00132640084685763, 0.00710420023519982, 0, 0, 0, 0.00892707151040531, 0.00601113984912163, 0.00151988814764435, 0.000805314039458531, 5.3175024047654e-05, 0.00349953563577393, 0.00760770139992997]
        expected_bflr_organ_tab = [0.010336087522799, 0.00672685692298227, 0.0102475759110439, 0.0398546845573618, 0.0156271185158691, 0.00621682000202202, 0.00272599897183932, 0.0118747630750596, 0.0787530945523227, 0, 0, 0, 0.158234889019718, 0.0375460730010646, 0.014583771669617, 0.00405662987375378, 0.00190535221652934, 0.00717423585325675, 0.0368031841285403, 0.0106698154370583, 0.00699805660127947, 0.0105852216439478, 0.0405187550995336, 0.0160405194231851, 0.00647588229696919, 0.00290122927557271, 0.0122373490998423, 0.0796752757656298, 0, 0, 0, 0.15952351265463, 0.0381899608817959, 0.0149807843495667, 0.00426650390218653, 0.00204591456371046, 0.00745723157191653, 0.0374393294199976, 0.0110104747590336, 0.0072761864388104, 0.0109297990971797, 0.0411897589396252, 0.0164608523356193, 0.00674187383304584, 0.00308338546908345, 0.0126068669418621, 0.0806043904783814, 0, 0, 0, 0.160819069930225, 0.0388407818918394, 0.0153847289377465, 0.00448330515883526, 0.00219339321889041, 0.00774715798924017, 0.0380824078369325]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "user_example3.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)

    def test_summary_report_user_example4(self):
        expected_risk_tab = ['Jan  1, 2012', ' ', 'Male', '1950', 'Cancer of the Exposed Organs', ' ', ' ', 0.00664263418144071, 0.0148010843607768, 0.0252534628522878, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0.00685903300546973, 0.0149738604304652, 0.0250688829216044, 0.442667135793779, 0.450005341986822, 0.45745443325635, 0.453291856778776, 0.464979202417288, 0.477337805351137]
        expected_elr_organ_tab = [1.20879419647711e-05, 5.98930637172444e-05, 6.36917619092893e-05, 0.00124688238939436, -2.33858786756586e-05, 0.000114987589300021, -5.64634239209596e-05, 3.84958186700789e-05, 0.000616961805306528, 0, 0, 0, -0.00551683133176992, 0.000633220830586041, 5.62990126981962e-05, 4.09219128583191e-05, 2.55515689210718e-06, 0.000232126700451308, 0.000537530613844325, 0.000133396064030226, 0.000254163489236454, 0.000575955585141818, 0.00375574513243249, 0.000122829266412431, 0.000934230800118198, -4.69324590430647e-06, 0.00024849503672482, 0.00152343886011925, 0, 0, 0, 0.0015872437875115, 0.00210690615265696, 0.000556331545391298, 0.000169482893499829, 1.12914725979554e-05, 0.00109226593150099, 0.00173400158930689, 0.000329463227672563, 0.000551841168683192, 0.00220137183270811, 0.00868959214383242, 0.000334356615420315, 0.00319798751484239, 4.36513711857641e-05, 0.000583112156575344, 0.00304371908534204, 0, 0, 0, 0.0106245222075466, 0.00457184655125923, 0.00154589391575855, 0.000387805984043816, 2.95874449500247e-05, 0.00288473084650565, 0.0034353251091985]
        expected_eflr_organ_tab = [1.25636839732379e-05, 6.22668624060224e-05, 6.62153494975071e-05, 0.00128662786084104, -2.43122589319221e-05, 0.00011113408150628, -5.8700945236849e-05, 4.00200776321424e-05, 0.000641292472724849, 0, 0, 0, -0.00530072947162345, 0.000646717837499705, 4.86301701684439e-05, 4.25429823434601e-05, 2.65636331527672e-06, 0.000236284595808133, 0.000558831437852629, 0.000138662294897773, 0.000264214144402221, 0.000598735413132508, 0.00386769409722486, 0.000127685752419206, 0.00090902241232022, -4.87915833239826e-06, 0.000258322112070291, 0.00158372033013613, 0, 0, 0, 0.00152524318361606, 0.00211054622146432, 0.00048695875543337, 0.000176179921183724, 1.1729141298679e-05, 0.0011174636591684, 0.00180256215002982, 0.000342510406916565, 0.000573590544401232, 0.0022885502888417, 0.00872688160435505, 0.000347604296934307, 0.00319249306536696, 4.5375027874107e-05, 0.000606131799184807, 0.00316419610592469, 0, 0, 0, 0.0102471399914669, 0.00458226148612304, 0.00137413266375372, 0.000403156115543159, 3.07513473404967e-05, 0.00295161506742901, 0.00357083578188023]
        expected_bflr_organ_tab = [0.010336087522799, 0.00672685692298227, 0.0102475759110439, 0.0398546845573618, 0.0156271185158691, 0.00621682000202202, 0.00272599897183932, 0.0118747630750596, 0.0787530945523227, 0, 0, 0, 0.158234889019718, 0.0375460730010646, 0.014583771669617, 0.00405662987375378, 0.00190535221652934, 0.00717423585325675, 0.0368031841285403, 0.0106698154370583, 0.00699805660127947, 0.0105852216439478, 0.0405187550995336, 0.0160405194231851, 0.00647588229696919, 0.00290122927557271, 0.0122373490998423, 0.0796752757656298, 0, 0, 0, 0.15952351265463, 0.0381899608817959, 0.0149807843495667, 0.00426650390218653, 0.00204591456371046, 0.00745723157191653, 0.0374393294199976, 0.0110104747590336, 0.0072761864388104, 0.0109297990971797, 0.0411897589396252, 0.0164608523356193, 0.00674187383304584, 0.00308338546908345, 0.0126068669418621, 0.0806043904783814, 0, 0, 0, 0.160819069930225, 0.0388407818918394, 0.0153847289377465, 0.00448330515883526, 0.00219339321889041, 0.00774715798924017, 0.0380824078369325]        
        self.assert_summary_results_from_template(os.path.join(self.TEST_XLS, "user_example4.xls"), expected_risk_tab, expected_elr_organ_tab, expected_eflr_organ_tab, expected_bflr_organ_tab)
