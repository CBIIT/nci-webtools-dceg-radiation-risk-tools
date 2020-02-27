

import uuid

from django.db import models
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

    num_doses = models.IntegerField(default=1)
    num_radon = models.IntegerField(default=0)
    irep_version = models.TextField()
    ade_version = models.TextField()    

    class Meta:
        ordering = ['-create_time']        

    def __str__(self):
        return str(self.id)
