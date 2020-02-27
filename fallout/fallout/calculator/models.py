

import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

class ExecutionState(models.Model):
    state_name = models.CharField(max_length=100)

    def __str__(self):
        return self.state_name

class ExecutionTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form_data = JSONField()
    state = models.ForeignKey(ExecutionState, on_delete=models.CASCADE, default=1)
    
    create_time = models.DateTimeField(default=timezone.now)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    
    response_code = models.IntegerField(default=0)
    response_content = models.TextField(default='')

    exception = models.TextField(default='')

    num_locations = models.IntegerField(default=1)
    mother_milk = models.TextField()
    thyroid_cancer = models.TextField()
    fallout_version = models.TextField()
    ade_version = models.TextField()    

    class Meta:
        ordering = ['-create_time']        

    def __str__(self):
        return str(self.id)

class StateManager(models.Manager):

    def get_by_natural_key(self, abbreviation):
        return self.get(abbreviation=abbreviation)

class State(models.Model):
    abbreviation = models.CharField(max_length=2, verbose_name=_('State Abbreviation'), db_index=True)
    name = models.CharField(max_length=100, verbose_name=_('State Name'))

    objects = StateManager()
    
    class Meta:
        unique_together = ('abbreviation', 'name',)
        ordering = ['name','abbreviation',]

    def __str__(self):
        return '%s (%s)' % (self.name, self.abbreviation,)

    def natural_key(self):
        return (self.abbreviation,)

class CountyManager(models.Manager):

    def get_by_natural_key(self, state, name):
        return self.get(name=name, state__abbreviation=state)

class County(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('County Name'), db_index=True)
    state = models.ForeignKey(State, verbose_name=_('State'), on_delete=models.CASCADE)
    has_map = models.BooleanField(default=False)

    objects = CountyManager()
    
    class Meta:
        unique_together = ('name','state',)
        verbose_name_plural = "counties"
        ordering = ['state','name']

    def __str__(self):
        return '%s, %s' % (self.name, self.state,)

    def natural_key(self):
        return self.state.natural_key() + (self.name,)

class MappedCountyRegionManager(models.Manager):

    def get_by_natural_key(self, name, state, county):
        return self.get(name=name, county__state__abbreviation=state, county__name=county)
    
class MappedCountyRegion(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('County Region Name'), db_index=True)
    county = models.ForeignKey(County, verbose_name=_('County'), on_delete=models.CASCADE)

    objects = MappedCountyRegionManager()
    
    class Meta:
        unique_together = ('name','county',)
        ordering = ['county','name']

    def __str__(self):
        return '%s, %s' % (self.name, self.county,)

    def natural_key(self):
        return (self.name,) + self.county.natural_key()