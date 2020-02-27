
import os
import tempfile
import xlrd
import datetime

from django import forms
from django.forms.formsets import BaseFormSet
from django.utils import timezone

from radrat.calculator.utils import get_current_request
from radrat.calculator.constants import *

class ContactForm(forms.Form):
    subject = forms.CharField(label='Subject', max_length=100, required=True,widget=forms.TextInput(attrs={'size':55}))
    message = forms.CharField(label='Comment', required=True,widget=forms.Textarea(attrs={'cols': '50', 'rows': '7'}))
    sender = forms.EmailField(label='Your e-mail address', required=True,widget=forms.TextInput(attrs={'size':55}))

integer_error_messages = lambda name: {'invalid': '%s must be a positive number.' % name,
                                       'required': '%s is required.' % name,
                                       'max_value': '' + name + ' must be less than or equal to %(limit_value)s.',
                                       'min_value': '' + name + ' must be greater than or equal to %(limit_value)s.', }

GENDER_CHOICES = (
    ('', '---'),
    ('Female', 'Female'),
    ('Male', 'Male'),
)

ORGAN_CHOICES = (
    ('', '---'),
    ('All Organs', 'Apply dose to all organs'),
    ('Oral Cavity and Pharynx', 'Oral Cavity and Pharynx'),
    ('Esophagus', 'Esophagus'),
    ('Stomach', 'Stomach'),
    ('Colon', 'Colon'),
    ('Rectum', 'Rectum'),
    ('Liver', 'Liver'),
    ('Gallbladder', 'Gallbladder'),
    ('Pancreas', 'Pancreas'),
    ('Lung', 'Lung'),
    ('Breast', 'Breast'),
    ('Ovary', 'Ovary'),
    ('Female Genitalia (less ovary)', 'Uterus'),
    ('All Male Genitalia', 'Prostate'),
    ('Bladder', 'Bladder'),
    ('Urinary organs (less bladder)', 'Kidney'),
    ('Nervous system', 'Brain/CNS'),
    ('Thyroid', 'Thyroid'),
    ('Other and ill-defined sites', 'Other and ill-defined sites'),
    ('Leukemia', 'Leukemia'),
)

BASELINE_CHOICES = (
    ('', '---'),
    ('usseer00_05', 'U.S. 2000-2005'),
    ('usseer00_05w', 'U.S. 2000-2005 White'),
    ('usseer00_05b', 'U.S. 2000-2005 Black'),
    ('france03_07', 'France 2003-2007'),
    ('spain03_07', 'Spain 2003-2007'),
    ('england11_12', 'England 2011-2012'),
    ('japan10', 'Japan 2010'),
    ('korea10', 'Korea 2010'),
    ('brazil01_05', 'Brazil 2001-2005'),
)

class PersonalInformation(forms.Form):
    gen_choice = forms.ChoiceField(label='Gender', required=True, choices=GENDER_CHOICES, initial=GENDER_CHOICES[0][0])
    by = forms.IntegerField(label='Birth Year', required=True, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4, 'maxlength':4}), error_messages=integer_error_messages('Birth Year'))
    baseline = forms.ChoiceField(label='Population', required=True, choices=BASELINE_CHOICES, initial=BASELINE_CHOICES[1][0], widget=forms.Select(attrs={'class':'', }))

    MAX_AGE_STANDARD = 120
    MAX_AGE_LIMITED = 100

    def clean(self):
        cleaned_data = self.cleaned_data
        if self._errors: return cleaned_data

        by = self.cleaned_data['by']
        baseline = self.cleaned_data['baseline']
        max_age = self.MAX_AGE_LIMITED if baseline in ['england11_12','japan10','korea10'] else self.MAX_AGE_STANDARD
        if abs(datetime.datetime.today().year - by) > max_age:
            self.add_error('baseline', 'Age is not allowed to be greater than %d years for this population' % max_age)

        return cleaned_data

class SmokingHistoryInformation(forms.Form):
    include_history = forms.BooleanField(label='Include Smoking History Adjustment', required=False, initial=False, label_suffix='')
    cpd_intensity_inp = forms.IntegerField(label='Cigarettes/Day', required=False, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4, 'maxlength':4}), error_messages=integer_error_messages('Cigarettes/Day'))
    start_smk_yr_inp = forms.IntegerField(label='Year Started Smoking', required=False, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4, 'maxlength':4}), error_messages=integer_error_messages('Year Started Smoking'))
    quit_smk_p_inp = forms.IntegerField(label='Year Quit Smoking', required=False, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4, 'maxlength':4}), error_messages=integer_error_messages('Year Started Smoking'))

    def clean(self):
        cleaned_data = self.cleaned_data
        '''exit now if field errors already exist'''
        if self._errors: return cleaned_data

        include_history = cleaned_data['include_history']
        personal = PersonalInformation(get_current_request().session.get(SESSION_FORM_KEY, {}))
        '''Validation is only performed when user has selected a specific population and selected to include smoking history.'''
        if include_history and personal.is_valid() and personal.cleaned_data['baseline'] == BASELINE_CHOICES[1][0]: # 'U.S. 2000-2005'
            cpd_intensity_inp = cleaned_data['cpd_intensity_inp']
            start_smk_yr_inp = cleaned_data['start_smk_yr_inp']
            quit_smk_p_inp = cleaned_data['quit_smk_p_inp']

            '''Since the user indicated that they are including smoking history, cpd_intensity_inp is now required.'''
            if cpd_intensity_inp is None:
                self.add_error('cpd_intensity_inp', integer_error_messages('Cigarettes/Day')['required'])
                return cleaned_data

            '''If the number of cigarettes per day is greater than zero, validate the year inputs.'''
            if cpd_intensity_inp > 0:
                if start_smk_yr_inp is None:
                    self.add_error('start_smk_yr_inp', integer_error_messages('Year Started Smoking')['required'])
                    return cleaned_data
                '''check start smoking / end smoking against birth date and each other'''
                by = personal.cleaned_data['by']
                if start_smk_yr_inp < by:
                    self.add_error('start_smk_yr_inp', "Year smoking started cannot be less than birth year.")
                if quit_smk_p_inp is not None:
                    if quit_smk_p_inp < start_smk_yr_inp:
                        self.add_error('quit_smk_p_inp', "Year smoking quit cannot be less than year smoking started.")
                    if quit_smk_p_inp < by:
                        self.add_error('quit_smk_p_inp', "Year smoking quit cannot be less than birth year.")
        return cleaned_data

DOSETYPE_CHOICES = (
    ('', '---'),
    ('Fixed Value', 'Fixed Value(value)'),
    ('Lognormal', 'Lognormal(median,gsd)'),
    ('Normal', 'Normal(mean,sd)'),
    ('Triangular', 'Triangular(min,mode,max)'),
    ('Logtriangular', 'Logtriangular(min,mode,max)'),
    ('Uniform', 'Uniform(min,max)'),
    ('Loguniform', 'Loguniform(min,max)'),
)

PARAM1_TITLE = 'Param1: For "Fixed Value"-enter value; For Lognormal-enter median; For Normal-enter mean; For Triangular-enter minimum; For Logtriangular-enter minimum; For Uniform-enter minimum; For Loguniform-enter minimum'
PARAM2_TITLE = 'Param2: For "Fixed Value"-leave blank; For Lognormal-enter gsdev; For Normal-enter standard deviation; For Triangular-enter mode; For Logtriangular-enter mode; For Uniform-enter maximum; For Loguniform-enter maximum'
PARAM3_TITLE = 'Param3: For Triangular-enter maximum; For Logtriangular-enter maximum; all others-leave blank'

def _clean_parameters_data(form, dose_name, dosetype_name='dosetype', doseparm1_name='doseparm1', doseparm2_name='doseparm2', doseparm3_name='doseparm3'):
    dosetype = form.cleaned_data.get(dosetype_name, None)
    doseparm1 = form.cleaned_data.get(doseparm1_name, None)
    doseparm2 = form.cleaned_data.get(doseparm2_name, None)
    doseparm3 = form.cleaned_data.get(doseparm3_name, None)

    if not dosetype:
        form._errors[dosetype_name] = form.error_class(["%s is required." % dose_name])
    if doseparm1 is None:
        form._errors[doseparm1_name] = form.error_class(["Parameter 1 is required."])
    elif dosetype == DOSETYPE_CHOICES[2][0]: # Lognormal
        if not doseparm1 > 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 must be greater than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[2][1],)])
        if doseparm2 is None:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[2][1],)])
        elif doseparm2 < 1:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[2][1],)])
    elif dosetype == DOSETYPE_CHOICES[3][0]: # Normal
        if doseparm1 < 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[3][1],)])
        if doseparm2 is None:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[3][1],)])
        elif doseparm2 < 0:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[3][1],)])
    elif dosetype == DOSETYPE_CHOICES[4][0]: # Triangular
        if doseparm1 < 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
        if doseparm2 is None:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
        elif doseparm2 < doseparm1:
            form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than parameter 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
        if doseparm3 is None:
            form._errors[doseparm3_name] = form.error_class(["Parameter 3 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
        elif doseparm2 and doseparm3 < doseparm2:
            form._errors[doseparm3_name] = form.error_class(["Parameter 3 can not be less than parameter 2 if %s is %s." % (dose_name, DOSETYPE_CHOICES[4][1],)])
    elif dosetype == DOSETYPE_CHOICES[5][0]: # Logtriangular
        if not doseparm1 > 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 must be greater than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[5][1],)])
        if doseparm2 is None:
           form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[5][1],)])
        elif doseparm2 < doseparm1:
           form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than parameter 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[5][1],)])
        if doseparm3 is None:
           form._errors[doseparm3_name] = form.error_class(["Parameter 3 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[5][1],)])
        elif doseparm2 and doseparm3 < doseparm2:
           form._errors[doseparm3_name] = form.error_class(["Parameter 3 can not be less than parameter 2 if %s is %s." % (dose_name, DOSETYPE_CHOICES[5][1],)])
    elif dosetype == DOSETYPE_CHOICES[6][0]: # Uniform
        if doseparm1 < 0:
            form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[6][1],)])
        if doseparm2 is None:
           form._errors[doseparm2_name] = form.error_class(["Parameter 2 is required if %s is %s." % (dose_name, DOSETYPE_CHOICES[6][1],)])
        elif doseparm2 < doseparm1:
           form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than parameter 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[6][1],)])
    elif dosetype == DOSETYPE_CHOICES[7][0]: # Loguniform
       if not doseparm1 > 0:
           form._errors[doseparm1_name] = form.error_class(["Parameter 1 must be greater than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[7][1],)])
       if doseparm2 is None:
          form._errors[doseparm2_name] = form.error_class(["Parameter 2 required if %s is %s." % (dose_name, DOSETYPE_CHOICES[7][1],)])
       elif doseparm2 < doseparm1:
          form._errors[doseparm2_name] = form.error_class(["Parameter 2 can not be less than parameter 1 if %s is %s." % (dose_name, DOSETYPE_CHOICES[7][1],)])
    elif dosetype == DOSETYPE_CHOICES[1][0]: # Fixed Value
       if doseparm1 < 0:
           form._errors[doseparm1_name] = form.error_class(["Parameter 1 can not be less than 0 if %s is %s." % (dose_name, DOSETYPE_CHOICES[1][1],)])
    else: pass

DOSE_UNTS = (
    ('Gy', 'Gy'),
    ('rad (cGy)', 'rad (cGy)'),
    ('mGy', 'mGy'),
    ('mrad', 'mrad'),
    # ('Sv', 'Sv'),
    # ('rem (cSv)', 'rem (cSv)'),
    # ('mSv', 'mSv'),
    # ('mrem', 'mrem'),
)

class DoseUnitsForm(forms.Form):
    dose_units = forms.ChoiceField(label='Organ Dose', required=True, initial=DOSE_UNTS[2][0], choices=DOSE_UNTS)

EXPRATE_CHOICES = (
    ('', '---'),
    ('a', 'acute'),
    ('c', 'chronic'),
)

class DoseExosureForm(forms.Form):
    event = forms.IntegerField(label='Exposure Event', required=False, initial=1, min_value=1, max_value=9999, widget=forms.TextInput(attrs={'size':4}), error_messages=integer_error_messages('Exposure Event'))
    yoe = forms.IntegerField(label='Exposure Year', required=False, initial=None, min_value=0, max_value=9999, widget=forms.TextInput(attrs={'size':4, 'maxlength':4}), error_messages=integer_error_messages('Exposure Year'))
    organ = forms.ChoiceField(label='Organ', required=False, initial=ORGAN_CHOICES[0][0], choices=ORGAN_CHOICES)
    exprate = forms.ChoiceField(label='Organ', required=False, initial=EXPRATE_CHOICES[0][0], choices=EXPRATE_CHOICES)
    dosetype = forms.ChoiceField(label='Organ Dose (mGy) Distribution', required=False, initial=DOSETYPE_CHOICES[0][0], choices=DOSETYPE_CHOICES, widget=forms.Select(attrs={'class':'dose-type', }))
    doseparm1 = forms.DecimalField(label='Parameter 1', required=False, initial=0, widget=forms.TextInput(attrs={'title':PARAM1_TITLE, 'size':3, 'class':'dose-param1', }), error_messages=integer_error_messages('Parameter 1'))
    doseparm2 = forms.DecimalField(label='Parameter 2', required=False, initial=0, widget=forms.TextInput(attrs={'title':PARAM2_TITLE, 'size':3, 'class':'dose-param2', }), error_messages=integer_error_messages('Parameter 2'))
    doseparm3 = forms.DecimalField(label='Parameter 3', required=False, initial=0, widget=forms.TextInput(attrs={'title':PARAM3_TITLE, 'size':3, 'class':'dose-param3', }), error_messages=integer_error_messages('Parameter 3'))

    def has_changed(self):
        '''override base class to indicate that form always changed -- otherwise all blank form will not be validated
           I think this is because non of the fields are defined as required.
        '''
        return True

    def clean(self):
        cleaned_data = self.cleaned_data
        # exit now if field errors already exist
        if self._errors: return cleaned_data

        # validate form against PersonalInformation form data
        personal = PersonalInformation(get_current_request().session.get(SESSION_FORM_KEY, {}))
        if personal.is_valid():
            gen_choice = personal.cleaned_data['gen_choice']
            by = personal.cleaned_data['by']
            event = self.cleaned_data.get('event', None)
            if not event:
                self._errors['event'] = self.error_class(["Exposure Event is required."])
            yoe = self.cleaned_data.get('yoe', None)
            if not yoe:
                self._errors['yoe'] = self.error_class(["Exposure Year is required."])
            elif yoe < by:
                self._errors['yoe'] = self.error_class(["Exposure year can not be before birth year."])
            organ = self.cleaned_data.get('organ', None)
            if not organ:
                self._errors['organ'] = self.error_class(["Organ is required."])
            elif organ in (ORGAN_CHOICES[11][0], ORGAN_CHOICES[12][0], ORGAN_CHOICES[13][0],) and gen_choice == GENDER_CHOICES[2][0]:
                self._errors['organ'] = 'Organ cannot be chosen for male gender.'
            elif organ in (ORGAN_CHOICES[14][0],) and gen_choice == GENDER_CHOICES[1][0]:
                self._errors['organ'] = 'Organ cannot be chosen for female gender.'
            if not self.cleaned_data.get('exprate', None):
                self._errors['exprate'] = self.error_class(["Exposure Rate is required."])

            # validate dose parameters
            _clean_parameters_data(self, 'Distribution Type')
        return cleaned_data

def get_year_today():
    return datetime.datetime.today().year

LEUKEMIA_MODEL_CHOICES = (
    ('', '---'),
    ('BEIR VII', 'BEIR VII'),
    ('HSU', 'HSU'),
)

THYROID_MODEL_CHOICES = (
    ('', '---'),
    ('BEIR VII', 'BEIR VII'),
    ('VEIGA', 'VEIGA'),
)

class AdvancedFeaturesForm(forms.Form):
    sample_size = forms.IntegerField(label='Simulation Sample Size', required=True, initial=300, min_value=2, max_value=32000, error_messages=integer_error_messages('Simulation Sample Size'))
    random_seed = forms.IntegerField(label='Random Seed', required=True, initial=99, min_value=0, max_value=100000000, error_messages=integer_error_messages('Random Seed'))
    year_today = forms.IntegerField(label='Current Year Setting', required=True, initial=get_year_today, min_value=1900, max_value=3000, error_messages=integer_error_messages('Current Year Setting'))
    ududtype = forms.ChoiceField(label='Distribution Type', required=True, choices=DOSETYPE_CHOICES, initial=DOSETYPE_CHOICES[1][0], widget=forms.Select(attrs={'class':'udud-type', }))
    ududparm1 = forms.DecimalField(label='Distribution Parameter 1', required=False, initial=1, widget=forms.TextInput(attrs={'class':'udud-param1', 'title':PARAM1_TITLE, 'size':4}))
    ududparm2 = forms.DecimalField(label='Distribution Parameter 2', required=False, initial=0, widget=forms.TextInput(attrs={'class':'udud-param2', 'title':PARAM2_TITLE, 'size':4}))
    ududparm3 = forms.DecimalField(label='Distribution Parameter 3', required=False, initial=0, widget=forms.TextInput(attrs={'class':'udud-param3', 'title':PARAM3_TITLE, 'size':4}))

    leukemia_choice = forms.ChoiceField(label='Leukemia Model', required=True, choices=LEUKEMIA_MODEL_CHOICES, initial=LEUKEMIA_MODEL_CHOICES[1][0], widget=forms.HiddenInput())
    thyroid_choice = forms.ChoiceField(label='Thyroid Model', required=True, choices=THYROID_MODEL_CHOICES, initial=THYROID_MODEL_CHOICES[1][0], widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AdvancedFeaturesForm, self).__init__(*args, **kwargs)

    # def has_changed(self):
    #    '''override base class to indicate that form always changed -- otherwise all blank form will not be validated
    #       I think this is because non of the fields are defined as required.
    #    '''
    #    return True

    def clean(self):
        cleaned_data = self.cleaned_data
        if self._errors: return cleaned_data
        # validate dose parameters
        _clean_parameters_data(self, 'Distribution Type', 'ududtype', 'ududparm1', 'ududparm2', 'ududparm3')
        return cleaned_data

class BaseDoseExosureFormSet(BaseFormSet):
    def get_execution_estimation(self, sample_size):
        # Estimate time to run ... roughly, it takes
        #  - 10 seconds to do 1000 simulations per each event for a single organ.
        #  - 30 seconds to do 1000 simulations per each event for 2 or more organs.
        # The number of exposed organs adds a minor constant, while the number of events is the primary multiplicator.
        if any(self.errors):
            return 0

        events = {}
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            event_no = form.cleaned_data['event']
            organ = form.cleaned_data['organ']
            if event_no in events:
                events[event_no]['multiple_organs'] = True
            else:
                events[event_no] = {'multiple_organs':(organ == ORGAN_CHOICES[1][0]), }

        estimation = 0
        for k, v in list(events.items()):
            estimation += ((40 if v['multiple_organs'] else 15) * sample_size) / 1000
        return estimation

    def clean(self):
        # check that the number of exposures does not exceed max
        if self.total_form_count() > MAXIMUM_DOSE_EXPOSURES:
            raise forms.ValidationError('The number of dose exposures defined exceeds maximum of %d.' % (MAXIMUM_DOSE_EXPOSURES,))

        advanced = AdvancedFeaturesForm(get_current_request().session.get(SESSION_FORM_KEY, {}))
        if any(self.errors) or not advanced.is_valid(): # Don't bother validating the formset unless each form is valid on its own
            return

        # perform error checks related to memory limitations
        max_event_no = 0
        multiple_organs = False
        current_organ = None
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            event_no = form.cleaned_data['event']
            max_event_no = event_no if event_no > max_event_no else max_event_no
            organ = form.cleaned_data['organ']
            if (current_organ is not None and current_organ != organ) or organ == ORGAN_CHOICES[1][0]:
                multiple_organs = True
            current_organ = organ
        sample_size = advanced.cleaned_data['sample_size']
        if multiple_organs and (sample_size * max_event_no > 30000):
            raise forms.ValidationError('For %d exposure events that contain exposures to multiple organs, the sample size of %d is too large. To perform this calculation, reduce the number of exposure events and/or the sample size.' % (max_event_no, sample_size,))

        validation_errors = []
        # perform error checks related to incorrect combination of years of exposure or organ selection for a given exposure event
        for i in range(0, self.total_form_count()):
            iform = self.forms[i]
            ievent = iform.cleaned_data['event']
            iorgan = iform.cleaned_data['organ']
            iyoe = iform.cleaned_data['yoe']
            for j in range(i + 1, self.total_form_count()):
                jform = self.forms[j]
                jevent = jform.cleaned_data['event']
                jorgan = jform.cleaned_data['organ']
                jyoe = jform.cleaned_data['yoe']
                if ievent == jevent:
                    if iorgan == jorgan:
                        validation_errors.append('The organ specified in row #%d must be different than the organ in row #%d for the same exposure event (#%d).' % (i + 1, j + 1, jevent,))
                    if iorgan == ORGAN_CHOICES[1][0]:
                        validation_errors.append('Since "All Organs" is selected in row #%d, an additional dose cannot be assigned to the organ in row #%d for the same exposure event (#%d).' % (i + 1, j + 1, jevent,))
                    if jorgan == ORGAN_CHOICES[1][0]:
                        validation_errors.append('Since "All Organs" is selected in row #%d, an additional dose cannot be assigned to the organ in row #%d for the same exposure event (#%d).' % (j + 1, i + 1, jevent,))
                    if iyoe != jyoe:
                        validation_errors.append('The year of exposure specified in row #%d must be equal to the year of exposure in row #%d for the same exposure event (#%d).' % (j + 1, i + 1, jevent,))
        if validation_errors:
            raise forms.ValidationError(validation_errors)

class UploadFileForm(forms.Form):
    file = forms.FileField()

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