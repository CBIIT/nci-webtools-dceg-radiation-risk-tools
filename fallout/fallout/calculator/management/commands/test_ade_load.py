from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import os
import sys
import datetime
from threading import Thread

from fallout.calculator.tests import ADETestCase
from fallout.calculator.models import County

class Command (BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--num', type=int, default=5)        
        parser.add_argument('--locations', type=int, default=3)        
        parser.add_argument('--state', default='ID')

    def handle(self, *args, **options):

        begin = datetime.datetime.now()
        for county in County.objects.filter(state__abbreviation='ID').order_by('name')[:options['num']]:
            t = Thread(target=ADETestCase.analysis_county, args=(county, options['locations']))
            t.start()
        print('Completed all in %s.' % (datetime.datetime.now() - begin))    
