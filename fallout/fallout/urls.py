"""fallout URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

from . import views
from fallout.calculator import views as calc_views

handler500 = 'fallout.calculator.views.server_error'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^update/$', TemplateView.as_view(template_name='update.html'), name='site-updates'),
    url(r'^getstarted/$', view=calc_views.get_started, name='get-started'),

    url(r'^inputs/$', view=calc_views.inputs, name='inputs'),
    url(r'^inputs/clear/$', view=calc_views.clear, name='clear-inputs'),
    url(r'^selectcounty/$', view=calc_views.select_county, name='select-county'),
    url(r'^getcounties/$', view=calc_views.get_counties, name='get-counties'),
    url(r'^execute/$', view=calc_views.queue_report, name='queue-report'),
    url(r'^execute/poll/$', view=calc_views.poll_execution, name='poll-execution'),
    url(r'^results/$', view=calc_views.summary_report, name='summary-report'),
    
    url(r'^help/begindate/$', TemplateView.as_view(template_name='help_begin_date.html'), name='help-begin-date'),
    url(r'^help/statecounty/$', TemplateView.as_view(template_name='help_state_county.html'), name='help-state-county'),
    url(r'^help/milkamount/$', TemplateView.as_view(template_name='help_milk_amount.html'), name='help-milk-amount'),
    url(r'^help/mgy/$', TemplateView.as_view(template_name='help_mgy.html'), name='help-mgy'),
    url(r'^help/uncertainty/$', TemplateView.as_view(template_name='help_uncertainty_range.html'), name='help-uncertainty-range'),

    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='site-about'),
    url(r'^contact/$', view=views.contact, name='contact'),
]
