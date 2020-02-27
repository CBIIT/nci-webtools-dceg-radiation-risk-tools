
import logging

from django import template
from django.utils.safestring import mark_safe

from radrat.calculator.templatetags import Smartround, Smartround4, Smartround5, get_chances_100000, condition_small_values

logger = logging.getLogger(__name__)

register = template.Library()

@register.tag
def render_organ_risks(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, organ_risks, header_lbl, lower_idx, mean_idx, upper_idx = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    #if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
    #    raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return Organ_Risks_Render(organ_risks, header_lbl, lower_idx, mean_idx, upper_idx)

class Organ_Risks_Render(template.Node):
    def __init__(self, organ_risks, header_lbl, lower_idx, mean_idx, upper_idx):
        self.organ_risks = template.Variable(organ_risks)
        self.header_lbl = header_lbl
        self.lower_idx = int(lower_idx)
        self.mean_idx = int(mean_idx)
        self.upper_idx = int(upper_idx)
        
    def render(self, context):
        try:
            organ_risks = self.organ_risks.resolve(context)
            if organ_risks[self.upper_idx] != 0:
                return mark_safe('<tr><th style="width:150px;">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (self.header_lbl[1:len(self.header_lbl)-1],
                                                                                                                 condition_small_values(Smartround(get_chances_100000(organ_risks[self.lower_idx]))),
                                                                                                                 condition_small_values(Smartround(get_chances_100000(organ_risks[self.mean_idx]))),
                                                                                                                 condition_small_values(Smartround(get_chances_100000(organ_risks[self.upper_idx]))),))
            else: return ''    
        except Exception as e:
            logger.error('Organ_Risks_Render failed with error: {}'.format(str(e)))
            return ''    

@register.tag
def render_future_risks(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, risk_tab = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    #if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
    #    raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return Future_Risks_Render(risk_tab)

class Future_Risks_Render(template.Node):
    def __init__(self, risk_tab):
        self.risk_tab = template.Variable(risk_tab)
        
    def get_rounded_value(self, risk_tab, risk_idx, round_idx):
        if get_chances_100000(risk_tab[risk_idx]) < 1000:
            return Smartround5(get_chances_100000(risk_tab[round_idx]))
        elif get_chances_100000(risk_tab[risk_idx]) >= 1000 and get_chances_100000(risk_tab[risk_idx]) < 10000:
            return Smartround4(get_chances_100000(risk_tab[round_idx]))
        elif get_chances_100000(risk_tab[risk_idx]) >= 10000:
            return Smartround(get_chances_100000(risk_tab[round_idx]))                    
        
    def render(self, context):
        try:
            risk_tab = self.risk_tab.resolve(context)
            rows = '<tr><th>Excess Future Risk**</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (condition_small_values(Smartround(get_chances_100000(risk_tab[19]))),
                                                                                                condition_small_values(Smartround(get_chances_100000(risk_tab[20]))),
                                                                                                condition_small_values(Smartround(get_chances_100000(risk_tab[21]))),
                                                                                                  )
            rows += '<tr><th>Baseline Future Risk**</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (condition_small_values(self.get_rounded_value(risk_tab, 20, 22)),
                                                                                                   condition_small_values(self.get_rounded_value(risk_tab, 20, 23)),
                                                                                                   condition_small_values(self.get_rounded_value(risk_tab, 20, 24)),
                                                                                                   )
            rows += '<tr><th>Total Future Risk**</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (condition_small_values(self.get_rounded_value(risk_tab, 20, 25)),
                                                                                                condition_small_values(self.get_rounded_value(risk_tab, 20, 26)),
                                                                                                condition_small_values(self.get_rounded_value(risk_tab, 20, 27)),
                                                                                                )
            return mark_safe(rows)
        except Exception as e:
            logger.error('Future_Risks_Render failed with error: {}'.format(str(e)))
            return ''    
