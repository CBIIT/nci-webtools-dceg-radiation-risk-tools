
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib import admin

from irep.calculator import views as calc_views

handler500 = 'irep.calculator.views.server_error'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
        
    url(r'^$', TemplateView.as_view(template_name='irep_nih.html'), name='index'),
    url(r'^getstarted/$', view=calc_views.get_started, name='get-started'),
    url(r'^update/$', TemplateView.as_view(template_name='update.html'), name='irep-updates'),
    url(r'^privacy/$', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    url(r'^contact/$', view=calc_views.contact, name='contact'),
    url(r'^accessibility/$', TemplateView.as_view(template_name='accessibility.html'), name='accessibility'),
    url(r'^model/inputs/$', view=calc_views.inputs, name='model-inputs'),
    url(r'^model/inputs/clear/$', view=calc_views.clear, name='clear-inputs'),
    url(r'^model/template/$', view=calc_views.upload_template, name='model-template'),
    url(r'^model/$', TemplateView.as_view(template_name='model/m1_top.html'), name='model-details'),
    url(r'^model/lung/$', TemplateView.as_view(template_name='model/lung.html'), name='model-lung'),
    url(r'^model/radon/$', TemplateView.as_view(template_name='model/radon.html'), name='model-radon'),
    url(r'^model/udud/$', TemplateView.as_view(template_name='model/udud.html'), name='model-udud'),
    url(r'^model/other/$', TemplateView.as_view(template_name='model/m121_err_other.html'), name='model-m121_err_other'),
    url(r'^model/other/dose/$', TemplateView.as_view(template_name='model/m123_Dose_sv.html'), name='model-m123_Dose_sv'),
    url(r'^model/other/dose/cgy/$', TemplateView.as_view(template_name='model/m1232_Dose_csv.html'), name='model-m1232_Dose_csv'),
    url(r'^model/other/dose/ref/$', TemplateView.as_view(template_name='model/m1233_ref_unc.html'), name='model-m1233_ref_unc'),
    url(r'^model/other/coefficients/$', TemplateView.as_view(template_name='model/m124_fin_adj_err.html'), name='model-m124_fin_adj_err'),
    
    url(r'^model/other/coefficients/m1241_calc/$', view=calc_views.m1241_calc, name='model-m1241_calc'),
    url(r'^model/other/coefficients/m1241_calc_notrunc/$', view=calc_views.m1241_calc_notrunc, name='model-m1241_calc_notrunc'),
    url(r'^model/other/coefficients/m1242_calc/$', view=calc_views.m1242_calc, name='model-m1242_calc'),
    url(r'^model/other/coefficients/m1243_calc/$', view=calc_views.m1243_calc, name='model-m1243_calc'),
    url(r'^model/other/coefficients/m1244_calc/$', view=calc_views.m1244_calc, name='model-m1244_calc'),
    url(r'^model/other/coefficients/m1245_calc/$', view=calc_views.m1245_calc, name='model-m1245_calc'),
    
    url(r'^execute/$', view=calc_views.queue_report, name='queue-report'),
    url(r'^execute/poll/$', view=calc_views.poll_execution, name='poll-execution'),
    url(r'^results/$', view=calc_views.summary_report, name='summary-report'),
    
    url(r'^model/help/help_rad_type/$', TemplateView.as_view(template_name='model/help/help_rad_type.html'), name='model-help_rad_type'),
    url(r'^model/help/help_distr/$', TemplateView.as_view(template_name='model/help/help_distr.html'), name='model-help_distr'),
    url(r'^model/help/help_external/$', TemplateView.as_view(template_name='model/help/help_external.html'), name='model-help_external'),
    url(r'^model/help/help_internal/$', TemplateView.as_view(template_name='model/help/help_internal.html'), name='model-help_internal'),
    url(r'^model/help/help_note1/$', TemplateView.as_view(template_name='model/help/help_note1.html'), name='model-help_note1'),
    url(r'^model/help/help_note1a/$', TemplateView.as_view(template_name='model/help/help_note1a.html'), name='model-help_note1a'),
    url(r'^model/help/help_note2/$', TemplateView.as_view(template_name='model/help/help_note2.html'), name='model-help_note2'),
    url(r'^model/help/help_note2a/$', TemplateView.as_view(template_name='model/help/help_note2a.html'), name='model-help_note2a'),
    url(r'^model/help/help_note3/$', TemplateView.as_view(template_name='model/help/help_note3.html'), name='model-help_note3'),
    url(r'^model/help/help_totaldose/$', TemplateView.as_view(template_name='model/help/help_totaldose.html'), name='model-help_totaldose'),
    url(r'^model/help/help_separatedoses/$', TemplateView.as_view(template_name='model/help/help_separatedoses.html'), name='model-help_separatedoses'),
]
