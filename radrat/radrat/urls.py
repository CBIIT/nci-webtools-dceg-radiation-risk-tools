from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib import admin

from radrat.calculator import views as calc_views

handler500 = 'radrat.calculator.views.server_error'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='radrat_nih.html'), name='index'),
    url(r'^getstarted/$', view=calc_views.get_started, name='get-started'),
    url(r'^update/$', TemplateView.as_view(template_name='update.html'), name='radrat-updates'),
    url(r'^privacy/$', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    url(r'^contact/$', view=calc_views.contact, name='contact'),
    url(r'^accessibility/$', TemplateView.as_view(template_name='accessibility.html'), name='accessibility'),
    url(r'^diff/$', TemplateView.as_view(template_name='diff_b7_radrat.html'), name='difference'),
    url(r'^tutorials/$', TemplateView.as_view(template_name='tutorials.html'), name='tutorials'),
    url(r'^model/inputs/$', view=calc_views.inputs, name='model-inputs'),
    url(r'^model/inputs/clear/$', view=calc_views.clear, name='clear-inputs'),
    url(r'^model/template/$', view=calc_views.upload_template, name='model-template'),
    url(r'^model/inputs/summary_report/$', view=calc_views.summary_report, name='model-summary-report'),
    url(r'^about/$', TemplateView.as_view(template_name='about_radrat.html'), name='about-radrat'),
    url(r'^model/help/help_distr_organ/$', TemplateView.as_view(template_name='model/help/help_distr_organ.html'), name='model-help_distr_organ'),
    url(r'^model/help/help_distr_udaf/$', TemplateView.as_view(template_name='model/help/help_distr_udaf.html'), name='model-help_distr_udaf'),
    url(r'^model/help/help_exposure_info/$', TemplateView.as_view(template_name='model/help/help_exposure_info.html'), name='model-help_exposure_info'),
    url(r'^model/help/help_exposure_rate/$', TemplateView.as_view(template_name='model/help/help_exposure_rate.html'), name='model-help_exposure_rate'),
    url(r'^model/help/help_organ_dose_units/$', TemplateView.as_view(template_name='model/help/help_organ_dose_units.html'), name='model-help_organ_dose_units'),    
    url(r'^model/help/help_population_info/$', TemplateView.as_view(template_name='model/help/help_population.html'), name='model-help_population_info'),
    
    url(r'^execute/$', view=calc_views.queue_report, name='queue-report'),
    url(r'^execute/poll/$', view=calc_views.poll_execution, name='poll-execution'),
    url(r'^results/$', view=calc_views.summary_report, name='summary-report'),    
]
