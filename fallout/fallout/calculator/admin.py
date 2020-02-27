from django.contrib import admin

from .models import State, County, MappedCountyRegion, ExecutionState, ExecutionTask

@admin.register(ExecutionState)
class ExecutionStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_name')

@admin.register(ExecutionTask)
class ExecutionTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'create_time', 'start_time', 'end_time', 'response_code', 'number_locations', 'fallout_version', 'ade_version',)
    list_filter = ('state',)

    def number_locations(self, obj):
         return obj.num_locations

    number_locations.empty_value_display = '0'

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name',)

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name','state', )
    list_filter = ('has_map','state',)

@admin.register(MappedCountyRegion)
class MappedCountyRegionAdmin(admin.ModelAdmin):
    list_display = ('name','county', )
    list_filter = ('county',)
