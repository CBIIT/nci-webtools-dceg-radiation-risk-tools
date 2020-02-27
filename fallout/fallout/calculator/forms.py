
import datetime
import calendar

from django import forms
from django.forms.formsets import BaseFormSet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from fallout.calculator.utils import get_current_request
from fallout.calculator.constants import MAXIMUM_LOCATIONS, SESSION_FORM_KEY
from .models import State, County, MappedCountyRegion

integer_error_messages = lambda name: {'invalid': '%s must be a positive number.' % name,
                                       'required': '%s is required.' % name,
                                       'max_value': '' + name + ' must be less than or equal to %(limit_value)s.',
                                       'min_value': '' + name + ' must be greater than or equal to %(limit_value)s.', }

GENDER_CHOICES = (
    ('', '---'),
    ('Female', 'Female'),
    ('Male', 'Male'),
)

MOTHERS_MILK_CHOICES = (
    ('', '---'),
    ('No', 'No'),
    ('Yes', 'Yes'),
    ('Not Sure', 'Not Sure'),
)

DIAGNOSED_CANCER_CHOICES = (
    ('', '---'),
    ('No', 'No'),
    ('Yes', 'Yes'),
)

class PersonalInformation(forms.Form):
    gender = forms.ChoiceField(label=_('Gender'), required=True, choices=GENDER_CHOICES, initial=GENDER_CHOICES[0][0])
    dob = forms.DateField(label=_('Date of Birth'), required=True, widget=forms.DateInput(attrs={'min':settings.MINIMUM_DOB.strftime('%Y-%m-%d'),'max':settings.MAXIMUM_DOB.strftime('%Y-%m-%d')}))
    spent_hours_outdoors = forms.BooleanField(label=_('Not Sure'), label_suffix='', required=False)
    hours_outdoors = forms.IntegerField(label=_('Average Hours Outdoors'), widget=forms.NumberInput(attrs={'min':0, 'max':24,}), required=False)
    mothers_milk_toggle = forms.ChoiceField(label="Did you consume mother's milk as an infant?", required=False, choices=MOTHERS_MILK_CHOICES, initial=MOTHERS_MILK_CHOICES[0][0], widget=forms.Select(attrs={'class':'', }), help_text=_("Did you consume mother's milk as an infant?"))    
    diagnosed_cancer = forms.ChoiceField(label="Have you been diagnosed with thyroid cancer?", required=True, choices=DIAGNOSED_CANCER_CHOICES, initial=DIAGNOSED_CANCER_CHOICES[0][0], widget=forms.Select(attrs={'class':'', }), help_text=_("Have you been diagnosed with thyroid cancer?"))
    diag_year = forms.IntegerField(label=_('Year diagnosed'), widget=forms.NumberInput(attrs={'min':1945,'max':9999}), required=False)

    def clean_dob(self):
        dob = self.cleaned_data['dob']
        if dob < settings.MINIMUM_DOB or dob > settings.MAXIMUM_DOB:
            self._errors['dob'] = self.error_class(["Date of birth must be between %d and %d." % (settings.MINIMUM_DOB.year,settings.MAXIMUM_DOB.year,)])   
        return dob

    def clean(self):
        cleaned_data = self.cleaned_data
        
        spent_hours_outdoors = self.cleaned_data.get('spent_hours_outdoors', None)
        hours_outdoors = self.cleaned_data.get('hours_outdoors', None)
        if not spent_hours_outdoors:
            if hours_outdoors in (None,'',):
                self._errors['hours_outdoors'] = self.error_class(["Average Hours Outdoors is required."])
            elif hours_outdoors < 0 or hours_outdoors > 24:         
                self._errors['hours_outdoors'] = self.error_class(["Average Hours Outdoors must be 0 to 24."])
        
        return cleaned_data

MONTHS = (
    ('', '---'),
    ('1', 'January'),
    ('2', 'February'),
    ('3', 'March'),
    ('4', 'April'),
    ('5', 'May'),
    ('6', 'June'),
    ('7', 'July'),
    ('8', 'August'),
    ('9', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
)

YEAR_CHOICES = lambda: [('', '---')] + [(str(y),str(y)) for y in range(settings.MINIMUM_BEGIN_DATE.year, settings.MAXIMUM_BEGIN_DATE.year + 1)]

MILK_SOURCE = (
    ('', '---'),
    ('Store Bought Cow Milk', 'Store Bought Cow Milk'),
    ('Backyard Cow Milk', 'Backyard Cow Milk'),
    ('Backyard Goat Milk', 'Goat Milk'),
    ('No Milk', 'No Cow or Goat Milk'),
)

MILK_AMOUNT = (
    ('', '---'),
    ('Light', 'Light'),
    ('Average', 'Average'),
    ('Heavy', 'Heavy'),
    ('No Milk', 'No Milk'),
)

def get_state_choices():
    return  [('', '---')] +  [(s.abbreviation, s.name) for s in State.objects.exclude(abbreviation__in=('OU','PR'))] + [(s.abbreviation, s.name) for s in State.objects.filter(abbreviation__in=('PR','OU',)).order_by('-abbreviation')]

def get_county_choices(state_abbr=None):
    counties = [('', '---')]
    if state_abbr:
        counties += [(c.name, c.name) for c in County.objects.filter(state__abbreviation=state_abbr)]
    else:
        counties += [(c.name, c.name) for c in County.objects.all()]
    return counties

def get_mapped_county_region_choices():
    return [(c.name, c.name.replace('_', ' ')) for c in MappedCountyRegion.objects.all()]
    
class StateCountyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StateCountyForm, self).__init__(*args, **kwargs)
        state_choices =  get_state_choices()
        self.fields['state'] = forms.ChoiceField(label='State', required=False, initial=state_choices[0][0], choices=state_choices, widget=forms.Select(attrs={'class':'state-select'}))
        county_choices =  get_county_choices()
        self.fields['county'] = forms.ChoiceField(label='County', required=False, initial=county_choices[0][0], choices=county_choices, widget=forms.Select(attrs={'class':'county-select'}))

minimum_history_date = datetime.date(1951, 1, 1)

class LocationForm(forms.Form):
    year = forms.ChoiceField(label='Year', required=False, initial=YEAR_CHOICES()[0][0], choices=YEAR_CHOICES(), widget=forms.Select(attrs={'class':'location-year'}))
    month = forms.ChoiceField(label='Month', required=False, initial=MONTHS[0][0], choices=MONTHS, widget=forms.Select(attrs={'class':'location-month'}))
    milksource = forms.ChoiceField(label='Milk Source', required=False, initial=MILK_SOURCE[0][0], choices=MILK_SOURCE, widget=forms.Select(attrs={'class':'location-milksource'}))
    milkamount = forms.ChoiceField(label='Milk Amount', required=False, initial=MILK_AMOUNT[0][0], choices=MILK_AMOUNT, widget=forms.Select(attrs={'class':'location-milkamount'}))

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        state_choices =  get_state_choices()
        self.fields['state'] = forms.ChoiceField(label='State', required=False, initial=state_choices[0][0], choices=state_choices, widget=forms.Select(attrs={'class':'location-state'}))
        county_choices =  get_county_choices() + get_mapped_county_region_choices()
        self.fields['county'] = forms.ChoiceField(label='County', required=False, initial=county_choices[0][0], choices=county_choices, widget=forms.Select(attrs={'class':'location-county'}))
        
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
            year = self.cleaned_data.get('year', None)
            if not year:
                self._errors['year'] = self.error_class(["Year is required."])
            month = self.cleaned_data.get('month', None)
            if not month:
                self._errors['month'] = self.error_class(["Month is required."])
            if year and month:                
                form_date = datetime.date(int(year), int(month), 1)
                if form_date < minimum_history_date:
                    self._errors['year'] = self.error_class(["Begin Date cannot be less than %s." % minimum_history_date.strftime('%m/%d/%Y')])
            
            state = self.cleaned_data.get('state', None)
            if not state:
                self._errors['state'] = self.error_class(["State is required."])
            county = self.cleaned_data.get('county', None)
            if not county and state is not None and state != 'OU':
                self._errors['county'] = self.error_class(["County is required if state is not outside study area."])
            milksource = self.cleaned_data.get('milksource', None)
            if not milksource:
                self._errors['milksource'] = self.error_class(["Milk Source is required."])
            milkamount = self.cleaned_data.get('milkamount', None)
            if not milkamount:
                self._errors['milkamount'] = self.error_class(["Milk Amount is required."])
            
            if milksource == 'No Milk' and milkamount != 'No Milk':
                self._errors['milkamount'] = self.error_class(["Milk Amount must be 'No Milk'."])
            
            #if not self._errors:
            #    dob = personal.cleaned_data['dob']            
            #    if dob > datetime.date(int(year), int(month), calendar.monthrange(int(year), int(month))[1]):
            #        self._errors['year'] = self.error_class([u"Begin date cannot be before date of birth."])

        return cleaned_data

class BaseLocationFormSet(BaseFormSet):
    def get_execution_estimation(self, sample_size):
        # Estimate time to run ... roughly 
        
        if any(self.errors):
            return 0
        
        '''Each entry adds approximately 100 seconds'''
        return self.total_form_count() * 100
    
    def clean(self):
        # check that the number of locations does not exceed max
        if self.total_form_count() > MAXIMUM_LOCATIONS:
            raise forms.ValidationError('The number of county locations / milk consumption history definitions exceed maximum of %d.' % (MAXIMUM_LOCATIONS,))

        personal = PersonalInformation(get_current_request().session.get(SESSION_FORM_KEY, {}))
        if not personal.is_valid():
            return 0

        if any(self.errors):
            return 0               
        
        dob = personal.cleaned_data['dob']
        dob_date = datetime.date(dob.year, dob.month, 1)
        validation_errors = []
        for i in range(0, self.total_form_count()):
            iform = self.forms[i]
            if iform.is_valid():
                iyear = iform.cleaned_data['year']
                imonth = iform.cleaned_data['month']
                idate = datetime.date(int(iyear), int(imonth), 1)
                if i ==0 and ((dob_date > minimum_history_date and idate != dob_date) or (dob_date < minimum_history_date and idate != minimum_history_date)):
                    validation_errors.append('The Begin Date in row #%d is required to match the greater of your birth month/year and January 1951.' % (i + 1,))
                
                for j in range(i + 1, self.total_form_count()):
                    jform = self.forms[j]
                    jyear = jform.cleaned_data['year']
                    jmonth = jform.cleaned_data['month']
                    jdate = datetime.date(int(jyear), int(jmonth), 1)
                    if jdate < idate:
                        validation_errors.append('The Begin Date in row #%d must be less than or equal to the Begin Date in row #%d.' % (i + 1, j + 1,))
        if validation_errors:
            raise forms.ValidationError(validation_errors)
