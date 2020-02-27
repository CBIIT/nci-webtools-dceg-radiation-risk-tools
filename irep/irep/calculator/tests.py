
import os
import unittest 
import requests

from django.test import TestCase
from django.conf import settings
from django.http import HttpRequest, QueryDict

from irep.calculator.views import get_session_parameters, SUMMARY_REPORT, UNCERTAINTY_REPORT, UPLOAD_TEMPLATE, MODEL_CALC
from irep.calculator.forms import PersonalInformation, LungCancerForm, DoseExosureForm, RadonExosureForm, AdvancedFeaturesForm, SkinCancerForm
from irep.calculator.forms import GENDER_CHOICES, CANCER_CHOICES, ETHNIC_CHOICES, EXPOSURE_SOURCE_CHOICES, SMOKING_HISTORY_CHOICES
from irep.calculator.forms import RADON_EXPRATE_CHOICES, DOSETYPE_CHOICES, EXPRATE_CHOICES, RADTYPE_CHOICES
from irep.calculator.constants import *
from irep.calculator.utils import _thread_locals

class BaseTestCase(TestCase):
    TEST_XLS = os.path.join(settings.BASE_DIR, '..', 'test', 'xls')
            
    def get_excel_template_parse(self, filename):
        '''Reads parameters from Excel file which is parsed by Windows server procedure.'''
        # Create an HttpRequest -- so that we can mimic behavior in actual view function.
        request = HttpRequest()
        request.session = {}                
        params = QueryDict(query_string='', mutable=True)
        files = {'template_nih.xls': open(filename, "rb")}
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UPLOAD_TEMPLATE), files=files, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()
        params.update(response_data['personal'])
        params.update(response_data['advanced'])
        params.update(response_data['skin_lung'])
        params.update(response_data['radon_exposure'])
        params.update(response_data['dose_exposure'])
        request.session[SESSION_FORM_KEY] = params
        return get_session_parameters(request)

    def get_default_params_dict(self):
        '''Create test collection of parameters.'''
        # Create an HttpRequest -- so that we can mimic behavior in actual view function.
        request = HttpRequest()
        request.session = {}
        postData = QueryDict(query_string='', mutable=True)
        postData.update({'gen_choice': GENDER_CHOICES[2][0], 'by': 1940, 'dod': 2000, 'cancer_choice': CANCER_CHOICES[1][0], })
        postData.update({'ethnic': ETHNIC_CHOICES[0][0], 'exposure_source': EXPOSURE_SOURCE_CHOICES[0][0], 'smoking_history': SMOKING_HISTORY_CHOICES[0][0], })
        postData.update({'radon_-TOTAL_FORMS': 1, 'radon_-INITIAL_FORMS': 0, 'radon_-MAX_NUM_FORMS': 200, 'radon_-0-yoe': 1980, 'radon_-0-exptype': RADON_EXPRATE_CHOICES[1][0], 'radon_-0-dosetype': DOSETYPE_CHOICES[1][0], 'radon_-0-doseparm1': 2, 'radon_-0-doseparm2': 2, 'radon_-0-doseparm3': 0, })
        postData.update({'dose_-TOTAL_FORMS': 1, 'dose_-INITIAL_FORMS': 0, 'dose_-MAX_NUM_FORMS': 200, 'dose_-0-yoe': 1980, 'dose_-0-exprate': EXPRATE_CHOICES[2][0], 'dose_-0-radtype': RADTYPE_CHOICES[5][0], 'dose_-0-dosetype': DOSETYPE_CHOICES[1][0], 'dose_-0-doseparm1': 2, 'dose_-0-doseparm2': 2, 'dose_-0-doseparm3': 0, })
        postData.update({'sample_size': 10000, 'random_seed': 99, 'ududtype': DOSETYPE_CHOICES[1][0], 'ududparm1': 1, 'ududparm2': 1, 'ududparm3': 0, })
        request.session[SESSION_FORM_KEY] = postData
        return get_session_parameters(request)

class BaseFormTests(BaseTestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.session = {}
        _thread_locals.request = self.request
        
    def baseline_PersonalInformation(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'gen_choice': GENDER_CHOICES[1][0], 'by': 1940, 'dod': 2000, 'cancer_choice': CANCER_CHOICES[1][0], })
        form = PersonalInformation(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data

    def baseline_LungCancerForm(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'exposure_source': EXPOSURE_SOURCE_CHOICES[1][0], 'smoking_history': SMOKING_HISTORY_CHOICES[1][0], })
        form = LungCancerForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data

    def baseline_SkinCancerForm(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'ethnic': ETHNIC_CHOICES[1][0], })
        form = SkinCancerForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data

    def baseline_DoseExosureForm(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'yoe':1980, 'exprate':EXPRATE_CHOICES[2][0], 'radtype':RADTYPE_CHOICES[5][0], 'dosetype':DOSETYPE_CHOICES[1][0], 'doseparm1':2, 'doseparm2':2, 'doseparm3':0, })
        form = DoseExosureForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data

    def baseline_RadonExosureForm(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'yoe':1980, 'exptype':RADON_EXPRATE_CHOICES[1][0], 'dosetype':DOSETYPE_CHOICES[1][0], 'doseparm1':2, 'doseparm2':2, 'doseparm3': 0, })
        form = RadonExosureForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data

    def baseline_AdvancedFeaturesForm(self):
        data = QueryDict(query_string='', mutable=True)
        data.update({'sample_size': 10000, 'random_seed': 99, 'ududtype': DOSETYPE_CHOICES[1][0], 'ududparm1': 1, 'ududparm2': 1, 'ududparm3': 0, })
        form = AdvancedFeaturesForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        return data
    
class PersonalInformationTests(BaseFormTests):
    def setUp(self):
        super(PersonalInformationTests, self).setUp()

    def test_dod(self):
        formData = self.baseline_PersonalInformation()
        formData.setlist('dod', [1940, ])
        form = PersonalInformation(data=formData)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))  
        formData.setlist('dod', [1939, ])
        form = PersonalInformation(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")   

    def test_cancer_choice(self):
        formData = self.baseline_PersonalInformation()
        # test that certain cancers fail if gender is male
        formData.setlist('gen_choice', [GENDER_CHOICES[2][0], ])
        for cancer_choice in (CANCER_CHOICES[15][0], CANCER_CHOICES[16][0], CANCER_CHOICES[17][0],):
            formData.setlist('cancer_choice', [cancer_choice, ])
            form = PersonalInformation(data=formData)
            self.assertFalse(form.is_valid(), "Form expectedly to have errors.")       
        # test that certain cancers fail if gender is female
        formData.setlist('gen_choice', [GENDER_CHOICES[1][0], ])
        for cancer_choice in (CANCER_CHOICES[18][0],):
            formData.setlist('cancer_choice', [cancer_choice, ])
            form = PersonalInformation(data=formData)
            self.assertFalse(form.is_valid(), "Form expectedly to have errors.")           

class LungCancerFormTests(BaseFormTests):
    def setUp(self):
        super(LungCancerFormTests, self).setUp()

    def test_exposure_source(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_LungCancerForm()
        # set to lung cancer
        data.setlist('cancer_choice', [CANCER_CHOICES[10][0], ]) 
        self.request.session[SESSION_FORM_KEY] = data
        # test that exposure_source is required for lung cancer
        formData.setlist('exposure_source', [EXPOSURE_SOURCE_CHOICES[0][0], ]) # set exposure_source to blank
        form = LungCancerForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")  

    def test_smoking_history(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_LungCancerForm()
        # set to lung cancer
        data.setlist('cancer_choice', [CANCER_CHOICES[10][0], ]) 
        self.request.session[SESSION_FORM_KEY] = data
        # test that smoking_history is required for lung cancer
        formData = self.baseline_LungCancerForm()
        formData.setlist('smoking_history', [SMOKING_HISTORY_CHOICES[0][0], ]) # set smoking_history to blank
        form = LungCancerForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")

class SkinCancerFormTests(BaseFormTests):
    def setUp(self):
        super(SkinCancerFormTests, self).setUp()

    def test_ethnic(self):
        data = self.baseline_PersonalInformation()
        self.request.session[SESSION_FORM_KEY] = data
        formData = self.baseline_SkinCancerForm()
        for skin_cancer in (CANCER_CHOICES[13][0], CANCER_CHOICES[14][0]):
            data.setlist('cancer_choice', [skin_cancer, ]) 
            self.request.session[SESSION_FORM_KEY] = data
            # test that ethnic is required for cancer
            formData.setlist('ethnic', [ETHNIC_CHOICES[0][0], ]) # set ethnic to blank
            form = SkinCancerForm(data=formData)
            self.assertFalse(form.is_valid(), "Form expectedly to have errors.")

class DoseExosureFormTests(BaseFormTests):
    def setUp(self):
        super(DoseExosureFormTests, self).setUp()

    def test_yoe(self):
        data = self.baseline_PersonalInformation()
        data.update(self.baseline_LungCancerForm())
        # set exposure_source to 'Other Sources'
        data.setlist('exposure_source', [EXPOSURE_SOURCE_CHOICES[2][0], ]) 
        self.request.session[SESSION_FORM_KEY] = data
        form = LungCancerForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))   
        # test that yoe is required
        formData = self.baseline_DoseExosureForm()
        formData.setlist('yoe', []) # set yoe to blank
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")    
        # test that yoe can not be before dod
        formData.setlist('yoe', [2001, ])
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")  

    def test_exprate(self):
        data = self.baseline_PersonalInformation()
        data.update(self.baseline_LungCancerForm())
        # set exposure_source to 'Other Sources'
        data.setlist('exposure_source', [EXPOSURE_SOURCE_CHOICES[2][0], ]) 
        self.request.session[SESSION_FORM_KEY] = data
        form = LungCancerForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        # test that exprate is required
        formData = self.baseline_DoseExosureForm()
        formData.setlist('exprate', [EXPRATE_CHOICES[0][0], ]) # set exprate to blank
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.") 

    def test_radtype(self):
        data = self.baseline_PersonalInformation()
        data.update(self.baseline_LungCancerForm())
        # set exposure_source to 'Other Sources'
        data.setlist('exposure_source', [EXPOSURE_SOURCE_CHOICES[2][0], ]) 
        self.request.session[SESSION_FORM_KEY] = data
        form = LungCancerForm(data=data)
        self.assertTrue(form.is_valid(), "Form not expectedly to have errors: %s" % str(form.errors))
        # test that radtype is required
        formData = self.baseline_DoseExosureForm()
        formData.setlist('radtype', [RADTYPE_CHOICES[0][0], ]) # set radtype to blank
        form = DoseExosureForm(data=formData)
        self.assertFalse(form.is_valid(), "Form expectedly to have errors.")  

class RadonExosureFormTests(BaseFormTests):
    def setUp(self):
        super(RadonExosureFormTests, self).setUp()

    def test_yoe(self):
        data = self.baseline_PersonalInformation()
        data.update(self.baseline_LungCancerForm())
        # set cancer to Lung
        data.setlist('cancer_choice', [CANCER_CHOICES[10][0], ])         
        for exposure_source in (EXPOSURE_SOURCE_CHOICES[1][0], EXPOSURE_SOURCE_CHOICES[3][0],):
            data.setlist('exposure_source', [exposure_source, ]) 
            self.request.session[SESSION_FORM_KEY] = data        
            # test that yoe is required
            formData = self.baseline_RadonExosureForm()
            formData.setlist('yoe', []) # set yoe to blank
            form = RadonExosureForm(data=formData)
            self.assertFalse(form.is_valid(), "Form expectedly to have errors.")
            # test that yoe can not be before dod
            formData.setlist('yoe', [2001, ])
            form = RadonExosureForm(data=formData)
            self.assertFalse(form.is_valid(), "Form expectedly to have errors.")       

    def test_exptype(self):
        data = self.baseline_PersonalInformation()
        data.update(self.baseline_LungCancerForm())
        # set cancer to Lung
        data.setlist('cancer_choice', [CANCER_CHOICES[10][0], ])
        for exposure_source in (EXPOSURE_SOURCE_CHOICES[1][0], EXPOSURE_SOURCE_CHOICES[3][0],):
            data.setlist('exposure_source', [exposure_source, ]) 
            self.request.session[SESSION_FORM_KEY] = data        
            # test that exprate is required
            formData = self.baseline_RadonExosureForm()
            formData.setlist('exptype', [EXPRATE_CHOICES[0][0], ]) # set exprate to blank
            form = RadonExosureForm(data=formData)
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
        self.assertTrue('skin_lung' in response_data, "Missing expected key 'skin_lung'.")
        self.assertTrue('dose_exposure' in response_data, "Missing expected key 'dose_exposure'.")   
        self.assertTrue('radon_exposure' in response_data, "Missing expected key 'radon_exposure'.")   
        self.assertTrue('advanced' in response_data, "Missing expected key 'advanced'.")   
            
    def test_excel_template_parse(self):
        files = {'template_nih.xls': open(os.path.join(os.path.join(settings.STATIC_ROOT, 'docs', 'template_nih.xls')), "rb")}
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UPLOAD_TEMPLATE), files=files, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()
        self.assert_expected_keys(response_data)
        
        # compare parsed template with form defaults -- which almost match
        self.assertEqual(response_data['personal'],
                         {'dod': 2000, 'by': 1940, 'gen_choice': 'Male', 'cancer_choice': 'Oral Cavity and Pharynx'},
                         "'personal' does not match expected values.")
        self.assertEqual(response_data['skin_lung'],
                         {'smoking_history': 'Never smoked', 'exposure_source': 'Other Sources', 'ethnic': 'US Population'},
                         "'LungCancerForm' does not match expected values.")
        self.assertEqual(response_data['dose_exposure'],
                         {'dose_-TOTAL_FORMS': 1, 'dose_-0-radtype': 'e1', 'dose_-MAX_NUM_FORMS': '', 'dose_-0-doseparm2': 2, 'dose_-0-doseparm3': 0, 'dose_-0-yoe': 1980, 'dose_-INITIAL_FORMS': 0, 'dose_-0-exprate': 'c', 'dose_-0-doseparm1': 2, 'dose_-0-dosetype': 'Lognormal'},
                         "'dose_exposure' does not match expected values.")
        self.assertEqual(response_data['radon_exposure'],
                         {'radon_-0-doseparm1': 2, 'radon_-0-yoe': 1971, 'radon_-0-doseparm2': 2, 'radon_-MAX_NUM_FORMS': '', 'radon_-TOTAL_FORMS': 1, 'radon_-0-exptype': 'annual', 'radon_-0-dosetype': 'Lognormal', 'radon_-INITIAL_FORMS': 0, 'radon_-0-doseparm3': 0},
                         "'radon_exposure' does not match expected values.")
        self.assertEqual(response_data['advanced'],
                         {'random_seed': 99, 'ududparm3': 0, 'ududparm2': 1, 'ududparm1': 1, 'sample_size': 2000, 'ududtype': 'Lognormal'},
                         "'advanced' does not match expected values.")

class Summary_Report_ASP_Tests(BaseTestCase):    
    def assert_expected_keys(self, response_data):
        self.assertTrue('sumidx_tab' in response_data, "Missing expected key 'sumidx_tab'.")
        self.assertTrue('summ_tab' in response_data, "Missing expected key 'summ_tab'.")
        self.assertTrue('messages' in response_data, "Missing expected key 'messages'.")        
    
        for member in ['1st', '2.5th', '5th', '10th', '25th', '50th', '75th', '90th', '95th', '97.5th', '99th']:
            self.assertIn(member, response_data['sumidx_tab'], "Missing expected value '%s' in sumidx_tab." % member)
    
    def test_summary_report_defaults(self):
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, SUMMARY_REPORT), data=self.get_default_params_dict(), headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()
        # check for expected keys
        self.assert_expected_keys(response_data)        
        # check expected 'summ_tab' values for default form values
        expected_summ_tab = ['0.000', '0.005', '0.016', '0.032', '0.074', '0.160', '0.331', '0.600', '0.855', '1.212', '1.748', '0.270']
        self.assertEqual(expected_summ_tab, response_data['summ_tab'], "'summ_tab' does not match expected values.")

    def check_summary_results(self, template, expected_summ_tab):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, template))
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, SUMMARY_REPORT), data=params, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()
        # check for expected keys
        self.assert_expected_keys(response_data)              
        # check expected 'summ_tab' values for default form values
        self.assertEqual(expected_summ_tab, response_data['summ_tab'], "'summ_tab' does not match expected values.\nobservered: %s\nexpected: %s" % (response_data['summ_tab'], expected_summ_tab))

    def test_summary_report_example1(self):
        expected_summ_tab = ['0.000', '0.604', '2.119', '3.951', '8.121', '14.036', '21.911', '31.445', '37.462', '44.244', '53.171', '18.475']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 01.xls"), expected_summ_tab)

    def test_summary_report_example2(self):
        expected_summ_tab = ['0.000', '0.273', '0.976', '1.786', '3.822', '6.943', '11.318', '17.373', '21.895', '26.410', '33.930', '9.397']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 02.xls"), expected_summ_tab)

    def test_summary_report_example3(self):
        expected_summ_tab = ['7.938', '11.528', '14.985', '18.941', '26.994', '37.213', '48.746', '57.442', '62.066', '66.317', '72.013', '42.058']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 03.xls"), expected_summ_tab)

    def test_summary_report_example4(self):
        expected_summ_tab = ['4.356', '9.068', '12.880', '16.850', '25.531', '36.143', '48.025', '57.145', '62.272', '67.060', '71.399', '41.180']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 04.xls"), expected_summ_tab)

    def test_summary_report_example5(self):
        expected_summ_tab = ['1.562', '2.134', '2.679', '3.424', '5.622', '9.506', '15.525', '24.107', '30.184', '35.887', '45.643', '13.418']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 05.xls"), expected_summ_tab)

    def test_summary_report_example6(self):
        expected_summ_tab = ['7.614', '9.306', '11.643', '14.950', '22.300', '32.727', '45.181', '56.814', '64.393', '70.399', '75.774', '40.245']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 06.xls"), expected_summ_tab)

    def test_summary_report_example7(self):
        expected_summ_tab = ['0.317', '0.515', '0.672', '1.095', '2.241', '4.622', '9.265', '15.796', '20.498', '25.541', '35.506', '7.849']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 07.xls"), expected_summ_tab)

    def test_summary_report_example8(self):
        expected_summ_tab = ['0.678', '0.932', '1.234', '1.774', '3.285', '8.526', '19.291', '30.747', '39.472', '45.352', '51.079', '15.455']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 08.xls"), expected_summ_tab)

    def test_summary_report_example9(self):
        expected_summ_tab = ['15.252', '20.918', '24.760', '31.155', '44.509', '58.781', '71.506', '79.706', '83.554', '87.153', '89.850', '65.965']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 09.xls"), expected_summ_tab)

    def test_summary_report_example10(self):
        expected_summ_tab = ['14.779', '21.211', '27.523', '35.461', '51.318', '66.479', '78.093', '84.981', '87.793', '90.983', '92.714', '73.080']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 10.xls"), expected_summ_tab)

    def test_summary_report_example11(self):
        expected_summ_tab = ['0.000', '0.000', '1.507', '6.547', '15.871', '33.062', '57.802', '73.865', '80.426', '84.373', '87.660', '52.182']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 11.xls"), expected_summ_tab)

    def test_summary_report_example12(self):
        expected_summ_tab = ['0.000', '0.000', '0.000', '0.000', '0.287', '13.117', '34.139', '55.790', '65.944', '76.163', '84.969', '33.708']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 12.xls"), expected_summ_tab)

    def test_summary_report_example13(self):
        expected_summ_tab = ['0.000', '0.000', '0.767', '2.080', '5.857', '13.522', '23.076', '33.964', '41.810', '48.015', '53.537', '18.611']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 13.xls"), expected_summ_tab)

    def test_summary_report_example14(self):
        expected_summ_tab = ['6.147', '8.587', '10.662', '13.808', '21.218', '31.056', '42.985', '55.150', '62.382', '66.937', '73.416', '38.036']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 14.xls"), expected_summ_tab)

    def test_summary_report_example15(self):
        expected_summ_tab = ['0.000', '0.000', '0.000', '0.033', '0.242', '0.750', '1.648', '2.968', '4.089', '5.132', '7.448', '1.255']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 15.xls"), expected_summ_tab)

    def test_summary_report_example16(self):
        expected_summ_tab = ['3.781', '4.649', '5.771', '7.466', '11.681', '19.022', '29.919', '40.935', '48.171', '54.999', '60.720', '25.113']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 16.xls"), expected_summ_tab)

    def test_summary_report_example17(self):
        expected_summ_tab = ['0.400', '1.149', '2.022', '3.685', '7.172', '12.673', '20.932', '31.335', '37.991', '44.127', '50.809', '17.419']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 17.xls"), expected_summ_tab)

    def test_summary_report_example18(self):
        expected_summ_tab = ['2.554', '4.023', '5.709', '7.932', '12.739', '21.964', '35.807', '53.807', '64.039', '72.044', '79.980', '34.411']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 18.xls"), expected_summ_tab)

    def test_summary_report_example19(self):
        expected_summ_tab = ['6.234', '8.121', '10.725', '14.773', '23.412', '37.523', '54.884', '68.758', '76.101', '82.174', '86.181', '49.985']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 19.xls"), expected_summ_tab)

    def test_summary_report_example20(self):
        expected_summ_tab = ['0.147', '0.235', '0.321', '0.533', '1.188', '2.833', '6.915', '14.692', '21.994', '29.873', '44.023', '7.154']
        self.check_summary_results(os.path.join(self.TEST_XLS, "Example 20.xls"), expected_summ_tab)
        
@unittest.skip("The intermediate report values are not reported and it is uncertain where Oakridge is maintaining them as updates occur.")        
class Intermediate_Report_ASP_Tests(BaseTestCase):
    def assert_expected_keys(self, params, response_data):
        self.assertTrue('unc_pc_tab' in response_data, "Missing expected key 'unc_pc_tab'.")
        if 'Radon' not in params.get('exposure_source', ()): 
            self.assertTrue('abs_dose_tab' in response_data, "Missing expected key 'abs_dose_tab'.")
            self.assertTrue('rbe_tab' in response_data, "Missing expected key 'rbe_tab'.")
            self.assertTrue('err_tab' in response_data, "Missing expected key 'err_tab'.")
            self.assertTrue('unc_shr_tab' in response_data, "Missing expected key 'unc_shr_tab'.")        
            self.assertTrue('unc_errsv_tab' in response_data, "Missing expected key 'unc_errsv_tab'.")
        if 'Other Sources' not in params.get('exposure_source', ()): 
            self.assertTrue('wlm_latency_tab' in response_data, "Missing expected key 'wlm_latency_tab'.")
            self.assertTrue('err_radon_tab' in response_data, "Missing expected key 'err_radon_tab'.")
            self.assertTrue('unc_rad_tab' in response_data, "Missing expected key 'unc_rad_tab'.")
        self.assertTrue('messages' in response_data, "Missing expected key 'messages'.")        
    
    def test_intermediate_report_defaults(self):
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UNCERTAINTY_REPORT), data=self.get_default_params_dict(), headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()        
        # check for expected keys
        self.assert_expected_keys(params, response_data)
        # check expected 'summ_tab' values for default form values
        expected_unc_pc_tab = [{'unc_pc_tab': '100.00%', 'unc_pc_idx_tab': 'ERR (sources other than radon)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'ERR (radon sources)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'User Defined Additional Uncertainty'}]
        self.assertEqual(expected_unc_pc_tab, response_data['unc_pc_tab'], "'unc_pc_tab' does not match expected values.\nobservered: %s\nexpected: %s" % (response_data['unc_pc_tab'], expected_unc_pc_tab))
        expected_abs_dose_tab = [['0.64', '2.00', '6.25']]
        self.assertEqual(expected_abs_dose_tab, response_data['abs_dose_tab'], "'abs_dose_tab' does not match expected values.\nobservered: %s\nexpected: %s" % (response_data['abs_dose_tab'], expected_abs_dose_tab))
        expected_rbe_tab = [['1.00', '1.00', '1.00']]
        self.assertEqual(expected_rbe_tab, response_data['rbe_tab'], "'rbe_tab' does not match expected values.\nobservered: %s\nexpected: %s" % (response_data['rbe_tab'], expected_rbe_tab))
        expected_err_tab = [['0.0002', '0.0016', '0.0087']]
        self.assertEqual(expected_err_tab, response_data['err_tab'], "'err_tab' does not match expected values.\nobservered: %s\nexpected: %s" % (response_data['err_tab'], expected_err_tab))
        expected_unc_shr_tab = [{'unc_shr_tab': '37.73%', 'unc_shr_idx_tab': 'Organ dose (cSv)'},
                                {'unc_shr_tab': '0.00%', 'unc_shr_idx_tab': 'Radiation Effectiveness Factor'},
                                {'unc_shr_tab': '62.27%', 'unc_shr_idx_tab': 'Adjusted ERR/Sv'}]
        self.assertEqual(expected_unc_shr_tab, response_data['unc_shr_tab'], "'unc_shr_tab' does not match expected values.\nobservered: %s\nexpected: %s" % (response_data['unc_shr_tab'], expected_unc_shr_tab))
        expected_unc_errsv_tab = [{'unc_errsv_idx_tab': 'Original ERR/Sv', 'unc_errsv_tab': '71.25%'},
                                  {'unc_errsv_idx_tab': 'Errors in dosimetry', 'unc_errsv_tab': '1.75%'},
                                  {'unc_errsv_idx_tab': 'Transfer to US Population', 'unc_errsv_tab': '2.38%'},
                                  {'unc_errsv_idx_tab': 'Dose and Dose Rate Effectiveness Factor - DDREF(low LET)', 'unc_errsv_tab': '24.62%'},
                                  {'unc_errsv_idx_tab': 'Adjustment for smoking (lung only)', 'unc_errsv_tab': '0.00%'}]
        self.assertEqual(expected_unc_errsv_tab, response_data['unc_errsv_tab'], "'unc_errsv_tab' does not match expected values.\nobservered: %s\nexpected: %s" % (response_data['unc_errsv_tab'], expected_unc_errsv_tab))

    def test_intermediate_report_example1(self):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, "Example 01.xls"))
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UNCERTAINTY_REPORT), data=params, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()        
        # check for expected keys
        self.assert_expected_keys(params, response_data)
        # check expected 'summ_tab' values for default form values
        expected_unc_pc_tab = [{'unc_pc_tab': '100.00%', 'unc_pc_idx_tab': 'ERR (sources other than radon)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'ERR (radon sources)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'User Defined Additional Uncertainty'}]
        self.assertEqual(expected_unc_pc_tab, response_data['unc_pc_tab'], "'unc_pc_tab' does not match expected values.")
        expected_abs_dose_tab = [['3.20', '10.00', '31.22'], ['10.27', '20.00', '38.93'], ['2.47', '15.00', '91.17'], ['7.71', '15.00', '29.20'], ['4.80', '15.00', '46.84']]
        self.assertEqual(expected_abs_dose_tab, response_data['abs_dose_tab'], "'abs_dose_tab' does not match expected values.")
        expected_rbe_tab = [['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00']]
        self.assertEqual(expected_rbe_tab, response_data['rbe_tab'], "'rbe_tab' does not match expected values.")
        expected_err_tab = [['0.0016', '0.0174', '0.1004'], ['0.0039', '0.0364', '0.1414'], ['0.0016', '0.0260', '0.2418'], ['0.0032', '0.0271', '0.1106'], ['0.0026', '0.0266', '0.1454']]
        self.assertEqual(expected_err_tab, response_data['err_tab'], "'err_tab' does not match expected values.")
        expected_unc_shr_tab = [{'unc_shr_tab': '14.11%', 'unc_shr_idx_tab': 'Organ dose (cSv)'},
                                {'unc_shr_tab': '0.00%', 'unc_shr_idx_tab': 'Radiation Effectiveness Factor'},
                                {'unc_shr_tab': '85.89%', 'unc_shr_idx_tab': 'Adjusted ERR/Sv'}]
        self.assertEqual(expected_unc_shr_tab, response_data['unc_shr_tab'], "'unc_shr_tab' does not match expected values.")
        expected_unc_errsv_tab = [{'unc_errsv_idx_tab': 'Original ERR/Sv', 'unc_errsv_tab': '65.44%'},
                                  {'unc_errsv_idx_tab': 'Errors in dosimetry', 'unc_errsv_tab': '1.88%'},
                                  {'unc_errsv_idx_tab': 'Transfer to US Population', 'unc_errsv_tab': '4.25%'},
                                  {'unc_errsv_idx_tab': 'Dose and Dose Rate Effectiveness Factor - DDREF(low LET)', 'unc_errsv_tab': '28.42%'},
                                  {'unc_errsv_idx_tab': 'Adjustment for smoking (lung only)', 'unc_errsv_tab': '0.00%'}]
        self.assertEqual(expected_unc_errsv_tab, response_data['unc_errsv_tab'], "'unc_errsv_tab' does not match expected values.")

    def test_intermediate_report_example2(self):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, "Example 02.xls"))
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UNCERTAINTY_REPORT), data=params, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()        
        # check for expected keys
        self.assert_expected_keys(params, response_data)
        # check expected 'summ_tab' values for default form values
        expected_unc_pc_tab = [{'unc_pc_tab': '100.00%', 'unc_pc_idx_tab': 'ERR (sources other than radon)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'ERR (radon sources)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'User Defined Additional Uncertainty'}]
        self.assertEqual(expected_unc_pc_tab, response_data['unc_pc_tab'], "'unc_pc_tab' does not match expected values.")
        expected_abs_dose_tab = [['3.20', '10.00', '31.22'], ['10.27', '20.00', '38.93'], ['2.47', '15.00', '91.17'], ['7.71', '15.00', '29.20'], ['4.80', '15.00', '46.84']]
        self.assertEqual(expected_abs_dose_tab, response_data['abs_dose_tab'], "'abs_dose_tab' does not match expected values.")
        expected_rbe_tab = [['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00']]
        self.assertEqual(expected_rbe_tab, response_data['rbe_tab'], "'rbe_tab' does not match expected values.")
        expected_err_tab = [['0.0008', '0.0079', '0.0463'], ['0.0017', '0.0168', '0.0648'], ['0.0007', '0.0118', '0.1114'], ['0.0015', '0.0123', '0.0500'], ['0.0012', '0.0122', '0.0665']]
        self.assertEqual(expected_err_tab, response_data['err_tab'], "'err_tab' does not match expected values.")
        expected_unc_shr_tab = [{'unc_shr_tab': '13.95%', 'unc_shr_idx_tab': 'Organ dose (cSv)'},
                                {'unc_shr_tab': '0.00%', 'unc_shr_idx_tab': 'Radiation Effectiveness Factor'},
                                {'unc_shr_tab': '86.05%', 'unc_shr_idx_tab': 'Adjusted ERR/Sv'}]
        self.assertEqual(expected_unc_shr_tab, response_data['unc_shr_tab'], "'unc_shr_tab' does not match expected values.")
        expected_unc_errsv_tab = [{'unc_errsv_idx_tab': 'Original ERR/Sv', 'unc_errsv_tab': '68.01%'},
                                  {'unc_errsv_idx_tab': 'Errors in dosimetry', 'unc_errsv_tab': '1.90%'},
                                  {'unc_errsv_idx_tab': 'Transfer to US Population', 'unc_errsv_tab': '2.45%'},
                                  {'unc_errsv_idx_tab': 'Dose and Dose Rate Effectiveness Factor - DDREF(low LET)', 'unc_errsv_tab': '27.65%'},
                                  {'unc_errsv_idx_tab': 'Adjustment for smoking (lung only)', 'unc_errsv_tab': '0.00%'}]
        self.assertEqual(expected_unc_errsv_tab, response_data['unc_errsv_tab'], "'unc_errsv_tab' does not match expected values.")

    def test_intermediate_report_example3(self):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, "Example 03.xls"))
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UNCERTAINTY_REPORT), data=params, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()        
        # check for expected keys
        self.assert_expected_keys(params, response_data)
        # check expected 'summ_tab' values for default form values
        expected_unc_pc_tab = [{'unc_pc_tab': '100.00%', 'unc_pc_idx_tab': 'ERR (sources other than radon)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'ERR (radon sources)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'User Defined Additional Uncertainty'}]
        self.assertEqual(expected_unc_pc_tab, response_data['unc_pc_tab'], "'unc_pc_tab' does not match expected values.")
        expected_abs_dose_tab = [['6.94', '11.34', '17.26'], ['15.50', '20.00', '24.50'], ['15.00', '15.00', '15.00'], ['12.54', '15.00', '17.46'], ['4.80', '15.00', '46.84']]
        self.assertEqual(expected_abs_dose_tab, response_data['abs_dose_tab'], "'abs_dose_tab' does not match expected values.")
        expected_rbe_tab = [['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00']]
        self.assertEqual(expected_rbe_tab, response_data['rbe_tab'], "'rbe_tab' does not match expected values.")
        expected_err_tab = [['0.0340', '0.1285', '0.4057'], ['0.0600', '0.2283', '0.6821'], ['0.0360', '0.1339', '0.3881'], ['0.0252', '0.0953', '0.2745'], ['0.0002', '0.0027', '0.0343']]
        self.assertEqual(expected_err_tab, response_data['err_tab'], "'err_tab' does not match expected values.")
        expected_unc_shr_tab = [{'unc_shr_tab': '0.30%', 'unc_shr_idx_tab': 'Organ dose (cSv)'},
                                {'unc_shr_tab': '0.00%', 'unc_shr_idx_tab': 'Radiation Effectiveness Factor'},
                                {'unc_shr_tab': '99.70%', 'unc_shr_idx_tab': 'Adjusted ERR/Sv'}]
        self.assertEqual(expected_unc_shr_tab, response_data['unc_shr_tab'], "'unc_shr_tab' does not match expected values.")
        expected_unc_errsv_tab = [{'unc_errsv_idx_tab': 'Original ERR/Sv', 'unc_errsv_tab': '59.14%'},
                                  {'unc_errsv_idx_tab': 'Errors in dosimetry', 'unc_errsv_tab': '1.54%'},
                                  {'unc_errsv_idx_tab': 'Transfer to US Population', 'unc_errsv_tab': '0.36%'},
                                  {'unc_errsv_idx_tab': 'Dose and Dose Rate Effectiveness Factor - DDREF(low LET)', 'unc_errsv_tab': '38.95%'},
                                  {'unc_errsv_idx_tab': 'Adjustment for smoking (lung only)', 'unc_errsv_tab': '0.00%'}]
        self.assertEqual(expected_unc_errsv_tab, response_data['unc_errsv_tab'], "'unc_errsv_tab' does not match expected values.")

    def test_intermediate_report_example4(self):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, "Example 04.xls"))
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, UNCERTAINTY_REPORT), data=params, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()        
        # check for expected keys
        self.assert_expected_keys(params, response_data)
        # check expected 'summ_tab' values for default form values
        expected_unc_pc_tab = [{'unc_pc_tab': '100.00%', 'unc_pc_idx_tab': 'ERR (sources other than radon)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'ERR (radon sources)'},
                               {'unc_pc_tab': '0.00%', 'unc_pc_idx_tab': 'User Defined Additional Uncertainty'}]
        self.assertEqual(expected_unc_pc_tab, response_data['unc_pc_tab'], "'unc_pc_tab' does not match expected values.")
        expected_abs_dose_tab = [['6.94', '11.34', '17.26'], ['15.50', '20.00', '24.50'], ['15.00', '15.00', '15.00'], ['12.54', '15.00', '17.46'], ['4.80', '15.00', '46.84']]
        self.assertEqual(expected_abs_dose_tab, response_data['abs_dose_tab'], "'abs_dose_tab' does not match expected values.")
        expected_rbe_tab = [['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00'], ['1.00', '1.00', '1.00']]
        self.assertEqual(expected_rbe_tab, response_data['rbe_tab'], "'rbe_tab' does not match expected values.")
        expected_err_tab = [['0.0281', '0.1231', '0.4079'], ['0.0517', '0.2154', '0.6682'], ['0.0305', '0.1265', '0.3782'], ['0.0212', '0.0903', '0.2737'], ['0.0001', '0.0025', '0.0333']]
        self.assertEqual(expected_err_tab, response_data['err_tab'], "'err_tab' does not match expected values.")
        expected_unc_shr_tab = [{'unc_shr_tab': '0.25%', 'unc_shr_idx_tab': 'Organ dose (cSv)'},
                                {'unc_shr_tab': '0.00%', 'unc_shr_idx_tab': 'Radiation Effectiveness Factor'},
                                {'unc_shr_tab': '99.75%', 'unc_shr_idx_tab': 'Adjusted ERR/Sv'}]
        self.assertEqual(expected_unc_shr_tab, response_data['unc_shr_tab'], "'unc_shr_tab' does not match expected values.")
        expected_unc_errsv_tab = [{'unc_errsv_idx_tab': 'Original ERR/Sv', 'unc_errsv_tab': '63.34%'},
                                  {'unc_errsv_idx_tab': 'Errors in dosimetry', 'unc_errsv_tab': '1.35%'},
                                  {'unc_errsv_idx_tab': 'Transfer to US Population', 'unc_errsv_tab': '0.21%'},
                                  {'unc_errsv_idx_tab': 'Dose and Dose Rate Effectiveness Factor - DDREF(low LET)', 'unc_errsv_tab': '35.10%'},
                                  {'unc_errsv_idx_tab': 'Adjustment for smoking (lung only)', 'unc_errsv_tab': '0.00%'}]
        self.assertEqual(expected_unc_errsv_tab, response_data['unc_errsv_tab'], "'unc_errsv_tab' does not match expected values.")
        
@unittest.skip("The model calculation report values are not reported and it is uncertain where Oakridge is maintaining them as updates occur.")                
class Model_Calculation_Report_ASP_Tests(BaseTestCase):
    def assert_expected_keys(self, response_data):
        self.assertTrue('summ_tab' in response_data, "Missing expected key 'summ_tab'.")
    
    def assert_expected(self, resultstype, params, expected_summ_tab):
        params['resultstype'] = resultstype 
        r = requests.post('%s%s' % (settings.WINDOWS_SERVER, MODEL_CALC), data=params, headers={'user-agent': 'Django App (%s)' % settings.BASE_URL,})
        self.assertEqual(r.status_code, 200, 'Unexpected response code: %d' % r.status_code)
        r.raise_for_status()
        response_data = r.json()        
        # check for expected keys
        self.assert_expected_keys(response_data)        
        # check expected 'summ_tab' values for default form values
        self.assertEqual(expected_summ_tab, response_data['summ_tab'], "'summ_tab' does not match expected values.")
    
    def test_model_calculation_defaults(self):
        params = self.get_default_params_dict()
        self.assert_expected('err_sv_original_p', params, [['0.00', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66']])
        self.assert_expected('err_sv_latency1_p', params, [['-0.01', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66']])
        self.assert_expected('err_sv_dosimetry_p', params, [['0.00', '0.01', '0.02', '0.05', '0.11', '0.17', '0.25', '0.35', '0.42', '0.49', '0.56']])
        self.assert_expected('err_sv_us_p', params, [['0.00', '0.01', '0.02', '0.04', '0.09', '0.14', '0.21', '0.30', '0.35', '0.42', '0.49']])
        self.assert_expected('err_sv_ddref_p', params, [['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.22', '0.28', '0.35', '0.45']])
        self.assert_expected('err_sv_individual_p', params, [['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.22', '0.28', '0.35', '0.45']])
        
    def test_model_calculation_example1(self):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, "Example 01.xls"))
        self.assert_expected('err_sv_original_p', params, [['0.00', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'],
                                                           ['0.00', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'],
                                                           ['0.00', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'],
                                                           ['0.00', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'],
                                                           ['0.00', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'], ])
        self.assert_expected('err_sv_latency1_p', params, [['-0.01', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'],
                                                           ['-0.01', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'],
                                                           ['-0.01', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'],
                                                           ['-0.01', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'],
                                                           ['-0.01', '0.02', '0.07', '0.15', '0.31', '0.48', '0.69', '0.95', '1.11', '1.27', '1.46'], ])
        self.assert_expected('err_sv_dosimetry_p', params, [['0.00', '0.02', '0.06', '0.12', '0.25', '0.40', '0.58', '0.81', '0.94', '1.07', '1.24'],
                                                            ['0.00', '0.02', '0.06', '0.12', '0.25', '0.40', '0.58', '0.81', '0.94', '1.07', '1.24'],
                                                            ['0.00', '0.02', '0.06', '0.12', '0.25', '0.40', '0.58', '0.81', '0.94', '1.07', '1.24'],
                                                            ['0.00', '0.02', '0.06', '0.12', '0.25', '0.40', '0.58', '0.81', '0.94', '1.07', '1.24'],
                                                            ['0.00', '0.02', '0.06', '0.12', '0.25', '0.40', '0.58', '0.81', '0.94', '1.07', '1.24'], ])
        self.assert_expected('err_sv_us_p', params, [['0.00', '0.01', '0.04', '0.09', '0.19', '0.31', '0.47', '0.64', '0.78', '0.90', '1.02'],
                                                     ['0.00', '0.01', '0.04', '0.09', '0.19', '0.31', '0.47', '0.64', '0.78', '0.90', '1.02'],
                                                     ['0.00', '0.01', '0.04', '0.09', '0.19', '0.31', '0.47', '0.64', '0.78', '0.90', '1.02'],
                                                     ['0.00', '0.01', '0.04', '0.09', '0.19', '0.31', '0.47', '0.64', '0.78', '0.90', '1.02'],
                                                     ['0.00', '0.01', '0.04', '0.09', '0.19', '0.31', '0.47', '0.64', '0.78', '0.90', '1.02'], ])
        self.assert_expected('err_sv_ddref_p', params, [['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'],
                                                        ['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'],
                                                        ['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'],
                                                        ['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'],
                                                        ['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'], ])
        self.assert_expected('err_sv_individual_p', params, [['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'],
                                                             ['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'],
                                                             ['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'],
                                                             ['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'],
                                                             ['0.00', '0.01', '0.02', '0.05', '0.10', '0.19', '0.31', '0.47', '0.60', '0.76', '0.93'], ])

    def test_model_calculation_example2(self):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, "Example 02.xls"))
        self.assert_expected('err_sv_original_p', params, [['0.00', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'],
                                                           ['0.00', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'],
                                                           ['0.00', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'],
                                                           ['0.00', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'],
                                                           ['0.00', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'], ])
        self.assert_expected('err_sv_latency1_p', params, [['-0.01', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'],
                                                           ['-0.01', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'],
                                                           ['-0.01', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'],
                                                           ['-0.01', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'],
                                                           ['-0.01', '0.01', '0.03', '0.06', '0.13', '0.21', '0.30', '0.42', '0.50', '0.57', '0.66'], ])
        self.assert_expected('err_sv_dosimetry_p', params, [['0.00', '0.01', '0.03', '0.05', '0.11', '0.17', '0.26', '0.36', '0.42', '0.48', '0.56'],
                                                            ['0.00', '0.01', '0.03', '0.05', '0.11', '0.17', '0.26', '0.36', '0.42', '0.48', '0.56'],
                                                            ['0.00', '0.01', '0.03', '0.05', '0.11', '0.17', '0.26', '0.36', '0.42', '0.48', '0.56'],
                                                            ['0.00', '0.01', '0.03', '0.05', '0.11', '0.17', '0.26', '0.36', '0.42', '0.48', '0.56'],
                                                            ['0.00', '0.01', '0.03', '0.05', '0.11', '0.17', '0.26', '0.36', '0.42', '0.48', '0.56'], ])
        self.assert_expected('err_sv_us_p', params, [['0.00', '0.01', '0.02', '0.04', '0.09', '0.14', '0.21', '0.30', '0.36', '0.41', '0.47'],
                                                     ['0.00', '0.01', '0.02', '0.04', '0.09', '0.14', '0.21', '0.30', '0.36', '0.41', '0.47'],
                                                     ['0.00', '0.01', '0.02', '0.04', '0.09', '0.14', '0.21', '0.30', '0.36', '0.41', '0.47'],
                                                     ['0.00', '0.01', '0.02', '0.04', '0.09', '0.14', '0.21', '0.30', '0.36', '0.41', '0.47'],
                                                     ['0.00', '0.01', '0.02', '0.04', '0.09', '0.14', '0.21', '0.30', '0.36', '0.41', '0.47'], ])
        self.assert_expected('err_sv_ddref_p', params, [['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'],
                                                        ['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'],
                                                        ['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'],
                                                        ['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'],
                                                        ['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'], ])
        self.assert_expected('err_sv_individual_p', params, [['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'],
                                                             ['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'],
                                                             ['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'],
                                                             ['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'],
                                                             ['0.00', '0.00', '0.01', '0.02', '0.05', '0.08', '0.14', '0.21', '0.27', '0.34', '0.43'], ])

    def test_model_calculation_example3(self):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, "Example 03.xls"))
        self.assert_expected('err_sv_original_p', params, [['0.48', '0.70', '0.90', '1.19', '1.69', '2.50', '3.47', '4.50', '5.34', '6.12', '6.76'],
                                                           ['0.41', '0.68', '0.87', '1.17', '1.75', '2.51', '3.44', '4.48', '5.17', '5.86', '6.89'],
                                                           ['0.32', '0.50', '0.70', '0.91', '1.36', '1.93', '2.62', '3.47', '3.96', '4.50', '5.31'],
                                                           ['0.26', '0.37', '0.48', '0.64', '0.96', '1.37', '1.88', '2.45', '2.88', '3.39', '4.00'],
                                                           ['0.00', '0.00', '0.00', '0.01', '0.01', '0.04', '0.10', '0.22', '0.33', '0.44', '0.60'], ])
        self.assert_expected('err_sv_latency1_p', params, [['0.48', '0.70', '0.90', '1.19', '1.69', '2.50', '3.47', '4.50', '5.34', '6.12', '6.76'],
                                                           ['0.41', '0.68', '0.87', '1.17', '1.75', '2.51', '3.44', '4.48', '5.17', '5.86', '6.89'],
                                                           ['0.32', '0.50', '0.70', '0.91', '1.36', '1.93', '2.62', '3.47', '3.96', '4.50', '5.31'],
                                                           ['0.26', '0.37', '0.48', '0.64', '0.96', '1.37', '1.88', '2.45', '2.88', '3.39', '4.00'],
                                                           ['0.00', '0.00', '0.00', '0.01', '0.01', '0.04', '0.10', '0.22', '0.33', '0.44', '0.60'], ])
        self.assert_expected('err_sv_dosimetry_p', params, [['0.36', '0.56', '0.74', '0.95', '1.39', '2.06', '2.89', '3.81', '4.49', '5.08', '6.00'],
                                                            ['0.34', '0.55', '0.71', '0.94', '1.43', '2.07', '2.88', '3.77', '4.38', '4.96', '6.05'],
                                                            ['0.26', '0.41', '0.57', '0.73', '1.10', '1.59', '2.20', '2.88', '3.34', '3.78', '4.63'],
                                                            ['0.20', '0.30', '0.39', '0.52', '0.79', '1.13', '1.57', '2.07', '2.43', '2.85', '3.47'],
                                                            ['0.00', '0.00', '0.00', '0.00', '0.01', '0.03', '0.08', '0.18', '0.29', '0.37', '0.52'], ])
        self.assert_expected('err_sv_us_p', params, [['0.33', '0.51', '0.68', '0.89', '1.29', '1.94', '2.69', '3.59', '4.18', '4.78', '5.58'],
                                                     ['0.32', '0.50', '0.66', '0.88', '1.32', '1.94', '2.67', '3.56', '4.08', '4.68', '5.54'],
                                                     ['0.24', '0.38', '0.52', '0.68', '1.02', '1.49', '2.05', '2.72', '3.12', '3.60', '4.21'],
                                                     ['0.19', '0.27', '0.36', '0.48', '0.73', '1.05', '1.46', '1.93', '2.26', '2.64', '3.23'],
                                                     ['0.00', '0.00', '0.00', '0.00', '0.01', '0.03', '0.07', '0.17', '0.26', '0.35', '0.48'], ])
        self.assert_expected('err_sv_ddref_p', params, [['0.16', '0.23', '0.32', '0.45', '0.71', '1.15', '1.80', '2.71', '3.48', '3.92', '4.99'],
                                                        ['0.16', '0.23', '0.32', '0.46', '0.72', '1.16', '1.79', '2.69', '3.44', '3.94', '4.94'],
                                                        ['0.12', '0.18', '0.25', '0.35', '0.55', '0.89', '1.37', '2.06', '2.63', '2.98', '3.76'],
                                                        ['0.09', '0.13', '0.17', '0.25', '0.40', '0.63', '0.99', '1.46', '1.86', '2.18', '2.84'],
                                                        ['0.00', '0.00', '0.00', '0.00', '0.01', '0.02', '0.05', '0.11', '0.18', '0.27', '0.36'], ])
        self.assert_expected('err_sv_individual_p', params, [['0.16', '0.23', '0.32', '0.45', '0.71', '1.15', '1.80', '2.71', '3.48', '3.92', '4.99'],
                                                             ['0.16', '0.23', '0.32', '0.46', '0.72', '1.16', '1.79', '2.69', '3.44', '3.94', '4.94'],
                                                             ['0.12', '0.18', '0.25', '0.35', '0.55', '0.89', '1.37', '2.06', '2.63', '2.98', '3.76'],
                                                             ['0.09', '0.13', '0.17', '0.25', '0.40', '0.63', '0.99', '1.46', '1.86', '2.18', '2.84'],
                                                             ['0.00', '0.00', '0.00', '0.00', '0.01', '0.02', '0.05', '0.11', '0.18', '0.27', '0.36'], ])

    def test_model_calculation_example4(self):
        params = self.get_excel_template_parse(os.path.join(self.TEST_XLS, "Example 04.xls"))
        self.assert_expected('err_sv_original_p', params, [['0.21', '0.44', '0.64', '0.89', '1.39', '2.11', '2.98', '3.96', '4.69', '5.41', '6.06'],
                                                           ['0.19', '0.43', '0.63', '0.88', '1.43', '2.11', '2.96', '3.94', '4.59', '5.20', '6.17'],
                                                           ['0.14', '0.32', '0.48', '0.69', '1.11', '1.63', '2.26', '3.03', '3.52', '4.00', '4.75'],
                                                           ['0.12', '0.24', '0.34', '0.49', '0.79', '1.15', '1.61', '2.16', '2.55', '3.03', '3.57'],
                                                           ['0.00', '0.00', '0.00', '0.00', '0.01', '0.03', '0.08', '0.19', '0.29', '0.39', '0.51'], ])
        self.assert_expected('err_sv_latency1_p', params, [['0.21', '0.44', '0.64', '0.89', '1.39', '2.11', '2.98', '3.96', '4.69', '5.41', '6.06'],
                                                           ['0.19', '0.43', '0.63', '0.88', '1.43', '2.11', '2.96', '3.94', '4.59', '5.20', '6.17'],
                                                           ['0.14', '0.32', '0.48', '0.69', '1.11', '1.63', '2.26', '3.03', '3.52', '4.00', '4.75'],
                                                           ['0.12', '0.24', '0.34', '0.49', '0.79', '1.15', '1.61', '2.16', '2.55', '3.03', '3.57'],
                                                           ['0.00', '0.00', '0.00', '0.00', '0.01', '0.03', '0.08', '0.19', '0.29', '0.39', '0.51'], ])
        self.assert_expected('err_sv_dosimetry_p', params, [['0.18', '0.35', '0.52', '0.72', '1.13', '1.73', '2.50', '3.35', '3.94', '4.55', '5.40'],
                                                            ['0.15', '0.35', '0.51', '0.71', '1.17', '1.74', '2.48', '3.31', '3.88', '4.39', '5.37'],
                                                            ['0.13', '0.26', '0.39', '0.56', '0.90', '1.33', '1.90', '2.54', '2.98', '3.38', '4.19'],
                                                            ['0.10', '0.19', '0.28', '0.39', '0.65', '0.95', '1.35', '1.81', '2.15', '2.52', '3.12'],
                                                            ['0.00', '0.00', '0.00', '0.00', '0.01', '0.03', '0.07', '0.16', '0.24', '0.32', '0.46'], ])
        self.assert_expected('err_sv_us_p', params, [['0.19', '0.37', '0.54', '0.76', '1.19', '1.82', '2.64', '3.50', '4.13', '4.86', '5.67'],
                                                     ['0.16', '0.36', '0.53', '0.74', '1.22', '1.83', '2.62', '3.45', '4.06', '4.69', '5.74'],
                                                     ['0.13', '0.28', '0.40', '0.58', '0.94', '1.40', '2.01', '2.65', '3.13', '3.61', '4.42'],
                                                     ['0.10', '0.20', '0.29', '0.42', '0.68', '0.99', '1.43', '1.90', '2.26', '2.68', '3.29'],
                                                     ['0.00', '0.00', '0.00', '0.00', '0.01', '0.03', '0.07', '0.16', '0.26', '0.33', '0.47'], ])
        self.assert_expected('err_sv_ddref_p', params, [['0.10', '0.16', '0.26', '0.40', '0.67', '1.10', '1.75', '2.65', '3.35', '4.02', '4.81'],
                                                        ['0.09', '0.16', '0.25', '0.40', '0.66', '1.11', '1.74', '2.63', '3.33', '3.95', '4.79'],
                                                        ['0.07', '0.13', '0.20', '0.31', '0.51', '0.86', '1.34', '2.02', '2.56', '3.03', '3.64'],
                                                        ['0.05', '0.09', '0.14', '0.22', '0.37', '0.61', '0.96', '1.43', '1.84', '2.19', '2.76'],
                                                        ['0.00', '0.00', '0.00', '0.00', '0.01', '0.02', '0.04', '0.11', '0.17', '0.26', '0.39'], ])
        self.assert_expected('err_sv_individual_p', params, [['0.10', '0.16', '0.26', '0.40', '0.67', '1.10', '1.75', '2.65', '3.35', '4.02', '4.81'],
                                                             ['0.09', '0.16', '0.25', '0.40', '0.66', '1.11', '1.74', '2.63', '3.33', '3.95', '4.79'],
                                                             ['0.07', '0.13', '0.20', '0.31', '0.51', '0.86', '1.34', '2.02', '2.56', '3.03', '3.64'],
                                                             ['0.05', '0.09', '0.14', '0.22', '0.37', '0.61', '0.96', '1.43', '1.84', '2.19', '2.76'],
                                                             ['0.00', '0.00', '0.00', '0.00', '0.01', '0.02', '0.04', '0.11', '0.17', '0.26', '0.39'], ])
