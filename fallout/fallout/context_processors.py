
from django.conf import settings

def fallout_context(request):
    return {
        'INCLUDE_WEB_ANALYTICS': settings.INCLUDE_WEB_ANALYTICS,
    }
