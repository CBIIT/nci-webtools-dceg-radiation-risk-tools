
import datetime, json, requests

from django.test import TestCase
from django.conf import settings

from .models import State, County, MappedCountyRegion
from .constants import SUMMARY_REPORT_ASP_TIMEOUT, SUMMARY_REPORT
from .forms import PersonalInformation, StateCountyForm, LocationForm

class ADETestCase(TestCase):
    '''Tests the execution of specific state/county combinations. This class is mostly for testing specific analyses
       that are causing problems or are in question. Each analysis takes ~ 1 minute and 30 seconds to execute -- with
       greater than 3,000 counties, the entire collection would take greater than 3 days to complete. 
    '''
    
    fixtures = ['counties.json',]

    @classmethod
    def add_location(cls, data, idx, county_name, state_abbreviation):
        data['location_-%d-month' % idx] = 1
        data['location_-%d-year' % idx] = (1951 + idx)
        data['location_-%d-state' % idx] = state_abbreviation
        data['location_-%d-county' % idx] = county_name
        data['location_-%d-milksource' % idx] = 'Store Bought Cow Milk'
        data['location_-%d-milkamount' % idx] = 'Average'
        data['location_-TOTAL_FORMS'] += 1
    
    @classmethod
    def get_parameters(cls, county_name, state_abbreviation, locations=1):
        kw = {'bda': 1, 'bmo': 1, 'byr': 1951, 'gender': 'Male', 
              'hours_outdoors': '0', 'Mothers_milk_toggle': 'Not Sure', 'diag_year': 2040,
              'location_-TOTAL_FORMS': 0,
              'randomseed': 99,
              'sample_size': 100,
              'web_flag': 1,
              'fallout_version': settings.FALLOUT_VERSION,
              'ade_version': settings.ADE_VERSION,
              'summary_rpt_timeout': SUMMARY_REPORT_ASP_TIMEOUT
              }

        for idx in range(0, locations):
            cls.add_location(kw, idx, county_name, state_abbreviation)
            
        return kw

    @classmethod
    def analysis_county(cls, county, locations=1):
        failed = 0
        if county.has_map:
            for countyregion in MappedCountyRegion.objects.filter(county=county):
                print('%s / %s' % (countyregion.name, county.state.abbreviation,))
                failed += cls.execute_analysis(cls.get_parameters(countyregion.name, county.state.abbreviation, locations), locations)
        else:
            print('%s / %s' % (county.name, county.state.abbreviation,))
            failed += cls.execute_analysis(cls.get_parameters(county.name, county.state.abbreviation, locations), locations)
        return failed
    
    @classmethod
    def execute_analysis(cls, data, locations=1):
        failed = False        
        
        try:
            start = datetime.datetime.now()
            r = requests.post('%s%s' % (settings.WINDOWS_SERVER, SUMMARY_REPORT), data=data, headers={'user-agent':'Django App (%s)' % settings.BASE_URL})
            if r.status_code != 200:
                failed = True
                print('Unable to complete operation (%d).' % r.status_code)
            else:
                response_data = json.loads(r.content) 
                failed == len(response_data['messages']) > 0
                print(str(response_data)) 
            print('Completed analysis in %s.' % (datetime.datetime.now() - start))
        except Exception as ex:
            failed = True
            print('Failed analysis: %s' % str(ex))
        
        return failed and 1 or 0
    
    def test_every_state_county(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.all().order_by('state__abbreviation', 'name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)
                
    def test_nevada_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='NV').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)    

    def test_montana_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='MT').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)

    def test_maryland_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='MD').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)

    def test_arizona_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='AZ').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)
                
    def test_arizona_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='AZ').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)                
    
    def test_new_mexico_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='NM').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)      
                
    def test_wyoming_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='WY').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)      
                
    def test_colorado_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='CO').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)

    def test_idaho_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='ID').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)

    def test_mapped_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(has_map=True).order_by('state__abbreviation', 'name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)    
        
    def test_outside_study_area(self):
        failed = 0
        data = self.get_parameters('OU', 'OU')
        begin = datetime.datetime.now()
        failed += self.execute_analysis(data)

        self.add_location(data, 1, 'Jefferson', 'NE')
        failed += self.execute_analysis(data)
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)        

    def test_high_risk_examples(self):
        '''The analyses provided by Oakridge as examples of high risk of thyroid cancer.'''
        failed = 0
        begin = datetime.datetime.now()
        
        data = self.get_parameters('Gunnison', 'CO')
        data['bmo'] = 4
        data['byr'] = 1952
        data['location_-0-month'] = 4
        data['location_-0-year'] = 1952
        data['location_-0-milksource'] = 'Backyard Cow Milk'
        data['location_-0-milkamount'] = 'Heavy'        
        failed += self.execute_analysis(data)

        data['location_-0-state'] = 'MT'
        data['location_-0-county'] = 'Meagher'
        data['location_-0-milksource'] = 'Backyard Goat Milk'
        failed += self.execute_analysis(data)

        data['location_-0-state'] = 'UT'
        data['location_-0-county'] = 'Salt Lake'
        data['location_-0-milksource'] = 'Store Bought Cow Milk'
        data['location_-0-milkamount'] = 'Average'        
        failed += self.execute_analysis(data)

        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed) 

    def test_born_1982_squish122(self):
        '''Tests analysis in which birth date is 1982 -- see squish https://www.squishlist.com/ims/rebcalc/122/.
        '''
        failed = 0
        begin = datetime.datetime.now()

        data = self.get_parameters('Cook', 'IL')
        data['bda'] = 3
        data['bmo'] = 1
        data['byr'] = 1982
        data['location_-0-month'] = 1
        data['location_-0-year'] = 1982
        data['location_-0-milksource'] = 'Store Bought Cow Milk'
        data['location_-0-milkamount'] = 'Average'   
        failed += self.execute_analysis(data)

        data = self.get_parameters('Cook', 'IL')
        data['bda'] = 31
        data['bmo'] = 12
        data['byr'] = 1982
        data['location_-0-month'] = 12
        data['location_-0-year'] = 1982
        data['location_-0-milksource'] = 'Store Bought Cow Milk'
        data['location_-0-milkamount'] = 'Average'   
        failed += self.execute_analysis(data)
        
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed) 
        print('Completed in %s.' % (datetime.datetime.now() - begin))

    def test_california_squish124(self):
        '''Tests Alameda, California -- see squish https://www.squishlist.com/ims/rebcalc/124/.
        '''
        failed = 0
        begin = datetime.datetime.now()
        data = self.get_parameters('Alameda', 'CA')
        data['bda'] = 19
        data['bmo'] = 12
        data['byr'] = 1944
        data['location_-0-month'] = 1
        data['location_-0-year'] = 1951
        data['location_-0-milksource'] = 'Store Bought Cow Milk'
        data['location_-0-milkamount'] = 'Average'   
        failed += self.execute_analysis(data)

        data = self.get_parameters('Lassen', 'CA')
        data['bda'] = 19
        data['bmo'] = 12
        data['byr'] = 1944
        data['location_-0-month'] = 1
        data['location_-0-year'] = 1951
        data['location_-0-milksource'] = 'Store Bought Cow Milk'
        data['location_-0-milkamount'] = 'Average'   
        failed += self.execute_analysis(data)

        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed) 
        print('Completed in %s.' % (datetime.datetime.now() - begin))

    def test_california_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='CA').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)

    def test_ohio_counties_squish128(self):
        '''Tests analysis in which born in counties Erie, Lorain, Ottawa and Richland of Ohio -- see squish https://www.squishlist.com/ims/rebcalc/128/.
        '''
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='OH', name__in=('Erie', 'Lorain', 'Ottawa', 'Richland',)).order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)

    def test_ohio_counties(self):
        failed = 0
        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='OH').order_by('name'):
            failed += self.analysis_county(county)
        
        print('Completed all in %s.' % (datetime.datetime.now() - begin))
        self.assertTrue(failed == 0, 'Unexpected reports failed: %d' % failed)


class PersonalInformationTestCase(TestCase):
    pass
