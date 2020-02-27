from django.contrib import admin

from .models import ExecutionState, ExecutionTask

@admin.register(ExecutionState)
class ExecutionStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_name')

@admin.register(ExecutionTask)
class ExecutionTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'create_time', 'start_time', 'end_time', 'response_code', 'num_doses', 'radrat_version', 'ade_version',)
    list_filter = ('state',)

    def number_locations(self, obj):
         return obj.num_locations

    number_locations.empty_value_display = '0'
