
from django.conf import settings

def irep_context(request):
    return {
        'INCLUDE_WEB_ANALYTICS': settings.INCLUDE_WEB_ANALYTICS,
    }
