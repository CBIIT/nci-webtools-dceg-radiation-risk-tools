
import os
import tempfile
import xlrd

from django import forms
from django.forms.formsets import BaseFormSet

from irep.calculator.utils import get_current_request
from irep.calculator.constants import *

class ContactForm(forms.Form):
    subject = forms.CharField(label='Subject', max_length=100, required=True,widget=forms.TextInput(attrs={'size':55}))
    message = forms.CharField(label='Comment', required=True,widget=forms.Textarea(attrs={'cols': '50', 'rows': '7'}))
    sender = forms.EmailField(label='Your e-mail address', required=True,widget=forms.TextInput(attrs={'size':55}))

integer_error_messages = lambda name: {'invalid': '%s must be a positive number.' % name,
                                       'required': '%s is required.' % name,
                                       'max_value': '' + name + ' must be less than or equal to %(limit_value)s.',
                                       'min_value': '' + name + ' must be greater than or equal to %(limit_value)s.',}

GENDER_CHOICES = (
    ('', '---'),
    ('Female', 'Female'),
    ('Male', 'Male'),
)

CANCER_CHOICES = (
    ('', '---'),
    ('Oral Cavity and Pharynx', 'Oral Cavity and Pharynx (140-149)'),
    ('Esophagus', 'Esophagus (150)'),
    ('Stomach', 'Stomach (151)'),
    ('Colon', 'Colon (153)'),
    ('Rectum', 'Rectum (154)'),
    ('All digestive', 'All digestive (150-159)'),
    ('Liver', 'Liver (155)'),
    ('Gallbladder', 'Gallbladder (156)'),
    ('Pancreas', 'Pancreas (157)'),
    ('Lung', 'Lung (162)'),
    ('Other respiratory', 'Other respiratory (160,161,163-165)'),
    ('Bone', 'Bone (170)'),
    ('Non-melanoma (BCC)', 'Non-melanoma skin-Basal Cell (173)'),
    ('Non-melanoma (SCC)', 'Non-melanoma skin-Squamous Cell (173)'),
    ('Breast', 'Female breast (174)'),
    ('Ovary', 'Ovary (183)'),
    ('Female Genitalia (less ovary)', 'Female Genitalia, excl. ovary(179-182,184)'),
    ('All Male Genitalia', 'All Male Genitalia (185-187)'),
    ('Bladder', 'Bladder (188)'),
    ('Urinary organs (less bladder)', 'Urinary organs, excluding bladder (189)'),
    ('Nervous system', 'Nervous system (191-192)'),
    ('Thyroid', 'Thyroid (193)'),
    ('Other and ill-defined sites', 'Ill-defined sites (170-172;174(male);175;190;194-199)'),
    ('Lymphoma and multiple myeloma', 'Lymphoma & multiple myeloma (200-203)'),
    ('Leukemia', 'Leukemia, excl. CLL (204-208,excl. 204.1)'),
    ('Acute Lymphocytic Leukemia', 'Acute Lymphocytic Leukemia (204.0)'),
    ('Acute Myeloid Leukemia', 'Acute Myeloid Leukemia (205.0)'),
    ('Chronic Myeloid Leukemia', 'Chronic Myeloid Leukemia (205.1)'),
)

class PersonalInformation(forms.Form):
    gen_choice = forms.ChoiceField(label='Gender', required=True, choices=GENDER_CHOICES, initial=GENDER_CHOICES[0][0])
    by = forms.IntegerField(label='Birth Year', required=True, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4}),error_messages=integer_error_messages('Birth Year'))
    dod = forms.IntegerField(label='Diagnosis Year', required=True, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4}),error_messages=integer_error_messages('Diagnosis Year'))
    cancer_choice = forms.ChoiceField(label='Cancer Model', required=True, choices=CANCER_CHOICES, initial=CANCER_CHOICES[0][0])

    def clean(self):
        cleaned_data = self.cleaned_data
        gen_choice = self.cleaned_data.get('gen_choice', None)
        by = self.cleaned_data.get('by', None)
        dod = self.cleaned_data.get('dod', None)
        cancer_choice = self.cleaned_data.get('cancer_choice', None)

        if gen_choice and cancer_choice:
            if gen_choice == GENDER_CHOICES[2][0] and cancer_choice in (CANCER_CHOICES[15][0],CANCER_CHOICES[16][0],CANCER_CHOICES[17][0],):
                self._errors['gen_choice'] = self.error_class(["Gender must be Female for selected cancer type."])
            if gen_choice == GENDER_CHOICES[1][0] and cancer_choice in (CANCER_CHOICES[18][0],):
                self._errors['gen_choice'] = self.error_class(["Gender must be Male for selected cancer type."])

        if dod and by and dod < by:
            self._errors['dod'] = self.error_class(["Year of diagnosis can not be before year of birth."])

        return cleaned_data

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = '<tr%(html_class_attr)s><th>%(label)s</th><td>%(field)s%(errors)s%(help_text)s</td></tr>',
            error_row = '<tr><td colspan="2">%s</td></tr>',
            row_ender = '</td></tr>',
            help_text_html = '<br />%s',
            errors_on_separate_row = False)

ETHNIC_CHOICES = (
    ('', '---'),
    ('US Population', 'All races/Race not specified'),
    ('American Indian', 'American Indian or Alaska Native'),
    ('Asian', 'Asian or Native Hawaiian or Other Pacific Islander'),
    ('Black', 'Black'),
    ('Hispanic', 'White-Hispanic'),
    ('White-non-hispanic', 'White-Non-Hispanic'),
)

EXPOSURE_SOURCE_CHOICES = (
    ('', '---'),
    ('Radon', 'Radon'),
    ('Other Sources', 'Other Sources'),
    ('Radon + Other Sources', 'Radon + Other Sources'),
)

SMOKING_HISTORY_CHOICES = (
    ('', '---'),
    ('Never smoked', 'Never smoked'),
    ('Former smoker', 'Former smoker'),
    ('Current smoker (? cig/day)', 'Current smoker (? cig/day)'),
    ('<10 cig/day (currently)', '<10 cig/day (currently)'),
    ('10-19 cig/day (currently)', '10-19 cig/day (currently)'),
    ('20-39 cig/day (currently)', '20-39 cig/day (currently)'),
    ('>40 cig/day (currently)', '40+ cig/day (currently)'),
)

class SkinCancerForm(forms.Form):
    ethnic = forms.ChoiceField(label='Racial/ethnic group', required=False, choices=ETHNIC_CHOICES, initial=ETHNIC_CHOICES[0][0])

    def clean(self):
        cleaned_data = self.cleaned_data
        if self._errors:
            return cleaned_data

        # validate form against PersonalInformation form data
        personal = PersonalInformation(get_current_request().session.get(SESSION_FORM_KEY, {}))
        if personal.is_valid():
            cancer_choice = personal.cleaned_data.get('cancer_choice', None)
            # skin form only for 'Non-melanoma (BCC)' and 'Non-melanoma (SCC)' cancers
            if cancer_choice in (CANCER_CHOICES[13][0],CANCER_CHOICES[14][0]):
                if not self.cleaned_data.get('ethnic', None):
                    self._errors['ethnic'] = self.error_class(["This field is required."])

        return cleaned_data

class LungCancerForm(forms.Form):
    exposure_source = forms.ChoiceField(label='Exposure from', required=False, choices=EXPOSURE_SOURCE_CHOICES, initial=EXPOSURE_SOURCE_CHOICES[0][0])
    smoking_history = forms.ChoiceField(label='Smoking history', required=False, choices=SMOKING_HISTORY_CHOICES, initial=SMOKING_HISTORY_CHOICES[0][0])

    def clean(self):
        cleaned_data = self.cleaned_data
        if self._errors:
            return cleaned_data

        # validate form against PersonalInformation form data
        personal = PersonalInformation(get_current_request().session.get(SESSION_FORM_KEY, {}))
        if personal.is_valid():
            cancer_choice = personal.cleaned_data.get('cancer_choice', None)
            # lung form only for 'Lung' cancer
            if cancer_choice in (CANCER_CHOICES[10][0],):
                if not self.cleaned_data.get('exposure_source', None):
                    self._errors['exposure_source'] = self.error_class(["This field is required."])
                if not self.cleaned_data.get('smoking_history', None):
                    self._errors['smoking_history'] = self.error_class(["This field is required."])

        return cleaned_data

DOSETYPE_CHOICES = (
    ('', '---'),
    ('Lognormal', 'Lognormal(median,gsdev)'),
    ('Normal', 'Normal(mean,sd)'),
    ('Triangular', 'Triangular(min,mode,max)'),
    ('Logtriangular', 'Logtriangular(min,mode,max)'),
    ('Uniform', 'Uniform(min,max)'),
    ('Loguniform', 'Loguniform(min,max)'),
    ('Constant', 'Constant(value)'),
)

RADON_EXPRATE_CHOICES = (
    ('', '---'),
    ('annual', 'Annual'),
    ('Total', 'Total'),
)

PARAM1_TITLE = 'Param1: For lognormal-enter median; For normal-enter mean; For triangular-enter minimum; For logtriangular-enter minimum; For uniform-enter minimum; For loguniform-enter minimum; For single value-enter value'
PARAM2_TITLE = 'Param2: For lognormal-enter gsdev; For normal-enter standard deviation; For triangular-enter mode; For logtriangular-enter mode; For uniform-enter maximum; For loguniform-enter maximum; For single value-leave blank'
PARAM3_TITLE = 'Param3: For triangular-enter maximum; For logtriangular-enter maximum; all others-leave blank'

def _clean_parameters_data(form, dose_name, dosetype_name='dosetype', doseparm1_name='doseparm1', doseparm2_name='doseparm2', doseparm3_name='doseparm3'):
    dosetype = form.cleaned_data.get(dosetype_name, None)
    doseparm1 = form.cleaned_data.get(doseparm1_name, None)
    doseparm2 = form.cleaned_data.get(doseparm2_name, None)
    doseparm3 = form.cleaned_data.get(doseparm3_name, None)

    if not dosetype:
        form._errors[dosetype_name] = form.error_class(["%s is required." % dose_name])
    if doseparm1 is None:
        form._errors[doseparm1_name] = form.error_class(["Parameter 1 is required."])
    elif dosetype == DOSETYPE_CHOICES[1][0]: # Lognormal
        if not doseparm1 > 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 must be greater than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[1][1],)])
        if doseparm2 is None:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[1][1],)])
        elif doseparm2 < 1:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[1][1],)])
    elif dosetype == DOSETYPE_CHOICES[2][0]: # Normal
        if doseparm1 < 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[2][1],)])
        if doseparm2 is None:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[2][1],)])
        elif doseparm2 < 0:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[2][1],)])
    elif dosetype == DOSETYPE_CHOICES[3][0]: # Triangular
        if doseparm1 < 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[3][1],)])
        if doseparm2 is None:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[3][1],)])
        elif doseparm2 < doseparm1:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than parameter 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[3][1],)])
        if doseparm3 is None:
            form._errors[doseparm3_name] = form.error_class(["Parameter 3 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[3][1],)])
        elif doseparm3 < doseparm2:
            form._errors[doseparm3_name] = form.error_class(["Parameter 3 can not be less than parameter 2 if %s is %s." % (dose_name, DOSETYPE_CHOICES[3][1],)])
    elif dosetype == DOSETYPE_CHOICES[4][0]: # Logtriangular
        if not doseparm1 > 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 must be greater than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
        if doseparm2 is None:
           form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
        elif doseparm2 < doseparm1:
           form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than parameter 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
        if doseparm3 is None:
           form._errors[doseparm3_name] = form.error_class(["Parameter 3 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
        elif doseparm2 and doseparm3 < doseparm2:
           form._errors[doseparm3_name] = form.error_class(["Parameter 3 can not be less than parameter 2 if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
    elif dosetype == DOSETYPE_CHOICES[5][0]: # Uniform
        if doseparm1 < 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[5][1],)])
        if doseparm2 is None:
           form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[5][1],)])
        elif doseparm2 < doseparm1:
           form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than parameter 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[5][1],)])
    elif dosetype == DOSETYPE_CHOICES[6][0]: # Loguniform
       if doseparm1 < 0:
           form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[6][1],)])
       if doseparm2 is None:
          form._errors[doseparm2_name] = form.error_class(["Parameter 2 required if %s is %s." % (dose_name, DOSETYPE_CHOICES[6][1],)])
       elif doseparm2 < doseparm1:
          form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than parameter 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[6][1],)])
    elif dosetype == DOSETYPE_CHOICES[7][0]: # Constant
       if doseparm1 < 0:
           form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[7][1],)])
    else: pass

class RadonExosureForm(forms.Form):
    yoe = forms.IntegerField(label='Exposure Year', required=False, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4}),error_messages=integer_error_messages('Exposure Year'))
    exptype = forms.ChoiceField(label='Exposure Type', required=False, initial=RADON_EXPRATE_CHOICES[1][0], choices=RADON_EXPRATE_CHOICES)
    dosetype = forms.ChoiceField(label='Exposure Distribution (WLM)', required=False, initial=DOSETYPE_CHOICES[0][0], choices=DOSETYPE_CHOICES, widget=forms.Select(attrs={'class':'radon-dose-type', }))
    doseparm1 = forms.DecimalField(label='WLM Parameter 1', required=False, initial=2, min_value=0, widget=forms.TextInput(attrs={'class':'radon-dose-param1','title':PARAM1_TITLE,'size':4}),error_messages=integer_error_messages('Parameter 1'))
    doseparm2 = forms.DecimalField(label='WLM Parameter 2', required=False, initial=2, min_value=0, widget=forms.TextInput(attrs={'class':'radon-dose-param2','title':PARAM2_TITLE,'size':4}),error_messages=integer_error_messages('Parameter 2'))
    doseparm3 = forms.DecimalField(label='WLM Parameter 3', required=False, initial=0, min_value=0, widget=forms.TextInput(attrs={'class':'radon-dose-param3','title':PARAM3_TITLE,'size':4}),error_messages=integer_error_messages('Parameter 3'))

    def has_changed(self):
        '''override base class to indicate that form always changed -- otherwise all blank form will not be validated
           I think this is because non of the fields are defined as required.
        '''
        return True

    def clean(self):
        cleaned_data = self.cleaned_data

        # validate form against PersonalInformation form data
        personal = PersonalInformation(get_current_request().session.get(SESSION_FORM_KEY, {}))
        lung_cancer = LungCancerForm(get_current_request().session.get(SESSION_FORM_KEY, {}))
        if personal.is_valid() and lung_cancer.is_valid():
            cancer_choice = personal.cleaned_data['cancer_choice']
            exposure_source = lung_cancer.cleaned_data['exposure_source']
            # only validate for select cancers (Lung) and exposure sources (Radon or Radon + Other Sources)
            if cancer_choice in (CANCER_CHOICES[10][0],) and exposure_source in (EXPOSURE_SOURCE_CHOICES[1][0],EXPOSURE_SOURCE_CHOICES[3][0],):
                # exit now if field errors already exist
                if self._errors: return cleaned_data
                by = personal.cleaned_data['by']
                dod = personal.cleaned_data['dod']
                yoe = self.cleaned_data.get('yoe', None)
                if not yoe:
                    self._errors['yoe'] = self.error_class(["Exposure Year is required."])
                elif yoe < by:
                    self._errors['yoe'] = self.error_class(["Exposure year can not be before birth year."])
                elif dod < yoe:
                    self._errors['yoe'] = self.error_class(["Exposure year can not be after diagnosis year."])
                if not self.cleaned_data.get('exptype', None):
                    self._errors['exptype'] = self.error_class(["Exposure Type is required."])
                #validate dose parameters
                _clean_parameters_data(self, 'Exposure Distribution')
            else:
                self._errors = None # clear any errors, we're not interested
        else:
            self._errors = None # clear any errors, we're not interested yet
        return cleaned_data

EXPRATE_CHOICES = (
    ('', '---'),
    ('a', 'acute'),
    ('c', 'chronic'),
)

RADTYPE_CHOICES = (
    ('', '---'),
    ('e1', 'electrons E<15keV'),
    ('e2', 'electrons E>15keV'),
    ('p1', 'photons E<30keV'),
    ('p2', 'photons E=30-250keV'),
    ('p3', 'photons E>250keV'),
    ('n1', 'neutrons E<10keV'),
    ('n2', 'neutrons E=10-100keV'),
    ('n3', 'neutrons E=100keV-2MeV'),
    ('n4', 'neutrons E=2-20MeV'),
    ('n5', 'neutrons E>20MeV'),
    ('a', 'alpha'),
)

class DoseExosureForm(forms.Form):
    yoe = forms.IntegerField(label='Exposure Year', required=False, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4}),error_messages=integer_error_messages('Exposure Year'))
    exprate = forms.ChoiceField(label='Exposure Rate', required=False, initial=EXPRATE_CHOICES[0][0], choices=EXPRATE_CHOICES)
    radtype = forms.ChoiceField(label='Selection of Radiation Type', required=False, initial=RADTYPE_CHOICES[0][0],  choices=RADTYPE_CHOICES)
    dosetype = forms.ChoiceField(label='Organ Dose (cSv)', required=False, initial=DOSETYPE_CHOICES[0][0], choices=DOSETYPE_CHOICES, widget=forms.Select(attrs={'class':'dose-type', }))
    doseparm1 = forms.DecimalField(label='Parameter 1', required=False, initial=2, widget=forms.TextInput(attrs={'class':'dose-param1', 'title':PARAM1_TITLE,'size':4}),error_messages=integer_error_messages('Parameter 1'))
    doseparm2 = forms.DecimalField(label='Parameter 2', required=False, initial=2, widget=forms.TextInput(attrs={'class':'dose-param2', 'title':PARAM2_TITLE,'size':4}),error_messages=integer_error_messages('Parameter 2'))
    doseparm3 = forms.DecimalField(label='Parameter 3', required=False, initial=0, widget=forms.TextInput(attrs={'class':'dose-param3', 'title':PARAM3_TITLE,'size':4}),error_messages=integer_error_messages('Parameter 3'))

    def has_changed(self):
        '''override base class to indicate that form always changed -- otherwise all blank form will not be validated
           I think this is because non of the fields are defined as required.
        '''
        return True

    def clean(self):
        cleaned_data = self.cleaned_data

        # validate form against PersonalInformation form data
        personal = PersonalInformation(get_current_request().session.get(SESSION_FORM_KEY, {}))
        lung_form = LungCancerForm(get_current_request().session.get(SESSION_FORM_KEY, {}))
        if personal.is_valid() and lung_form.is_valid():
            cancer_choice = personal.cleaned_data['cancer_choice']
            dod = personal.cleaned_data['dod']
            by = personal.cleaned_data['by']
            exposure_source = lung_form.cleaned_data['exposure_source']
            # general exposure forms only all cancers except 'Lung' cancer with 'Radon' only
            if not (cancer_choice in (CANCER_CHOICES[10][0],) and exposure_source in (EXPOSURE_SOURCE_CHOICES[1][0],)):
                # exit now if field errors already exist
                if self._errors: return cleaned_data
                yoe = self.cleaned_data.get('yoe', None)
                if not yoe:
                    self._errors['yoe'] = self.error_class(["Exposure Year is required."])
                elif yoe < by:
                    self._errors['yoe'] = self.error_class(["Exposure year can not be before birth year."])
                elif dod < yoe:
                    self._errors['yoe'] = self.error_class(["Exposure year can not be after diagnosis year."])
                if not self.cleaned_data.get('exprate', None):
                    self._errors['exprate'] = self.error_class(["Exposure Rate is required."])
                if not self.cleaned_data.get('radtype', None):
                    self._errors['radtype'] = self.error_class(["Radiation Type is required."])
                #validate dose parameters
                _clean_parameters_data(self, 'Organ Dose')
            else:
                self._errors = None # clear any errors, we're not interested
        else:
            self._errors = None # clear any errors, we're not interested yet
        return cleaned_data

class AdvancedFeaturesForm(forms.Form):
    sample_size = forms.IntegerField(label='Simulation Sample Size', required=True, initial=10000, min_value=2, max_value=32000, error_messages=integer_error_messages('Simulation Sample Size'))
    random_seed = forms.IntegerField(label='Random Seed', required=True, initial=99, min_value=0, max_value=100000000, error_messages=integer_error_messages('Random Seed'))
    ududtype = forms.ChoiceField(label='Distribution Type', required=True, choices=DOSETYPE_CHOICES, initial=DOSETYPE_CHOICES[1][0], widget=forms.Select(attrs={'class':'udud-type', }) )
    ududparm1 = forms.DecimalField(label='Distribution Parameter 1', required=False, initial=1, widget=forms.TextInput(attrs={'class':'udud-param1', 'title':PARAM1_TITLE,'size':4}))
    ududparm2 = forms.DecimalField(label='Distribution Parameter 2', required=False, initial=1, widget=forms.TextInput(attrs={'class':'udud-param2', 'title':PARAM2_TITLE,'size':4}))
    ududparm3 = forms.DecimalField(label='Distribution Parameter 3', required=False, initial=0, widget=forms.TextInput(attrs={'class':'udud-param3', 'title':PARAM3_TITLE,'size':4}))
    report_intermediate = forms.BooleanField(label='Intermediate Results', required=False, widget=forms.CheckboxInput(attrs={'class':'rpt_option',}))

    #def has_changed(self):
    #    '''override base class to indicate that form always changed -- otherwise all blank form will not be validated
    #       I think this is because non of the fields are defined as required.
    #    '''
    #    return True

    def clean(self):
        cleaned_data = self.cleaned_data
        if self._errors: return cleaned_data
        #validate dose parameters
        _clean_parameters_data(self, 'Distribution Type', 'ududtype', 'ududparm1', 'ududparm2', 'ududparm3')
        return cleaned_data

class BaseRadonExosureFormSet(BaseFormSet):

    def clean(self):
        # check that the number of exposures does not exceed max
        if self.total_form_count() > MAXIMUM_RADON_EXPOSURES:
            raise forms.ValidationError('The number of radon exposures defined exceeds maximum of %d.' % (MAXIMUM_RADON_EXPOSURES,))

        if any(self.errors): # Don't bother validating the formset unless each form is valid on its own
            return

class BaseDoseExosureFormSet(BaseFormSet):

    def clean(self):
        # check that the number of exposures does not exceed max
        if self.total_form_count() > MAXIMUM_DOSE_EXPOSURES:
            raise forms.ValidationError('The number of dose exposures defined exceeds maximum of %d.' % (MAXIMUM_DOSE_EXPOSURES,))

        if any(self.errors): # Don't bother validating the formset unless each form is valid on its own
            return

class UploadFileForm(forms.Form):
    file  = forms.FileField()
    
    def clean(self):
        file = self.cleaned_data['file']
        # Test that file is really an Excel file, in particular an .xls file.
        # This is a rough first check on the file - to protect against bad/malicious files.
        try:
            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(file.read())
            wb = xlrd.open_workbook(tmp)
        except xlrd.XLRDError:
            self.add_error('file', 'File does not appear to be a valid .xls file.')
        finally:
            os.unlink(tmp)  # delete the temp file no matter what
        file.seek(0)

