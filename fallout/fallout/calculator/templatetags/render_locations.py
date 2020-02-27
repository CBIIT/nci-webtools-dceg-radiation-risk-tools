
from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()

from fallout.calculator.templatetags.data_verbose import data_verbose

@register.tag
def render_locations(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, location_forms = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    #if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
    #    raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return Locations_Render(location_forms)

class Locations_Render(template.Node):
    def __init__(self, location_forms):
        self.location_forms = template.Variable(location_forms)
        
    def get_time_period(self, idx, form, location_forms):
        if idx == len(location_forms):
            return '%s / %s to %s' % (data_verbose(form['month']),
                                      data_verbose(form['year']),
                                      settings.MAXIMUM_BEGIN_DATE.strftime("%B / %Y"))
        else:
            next_form = location_forms[idx]
            return '%s / %s to %s / %s' % (data_verbose(form['month']),
                                           data_verbose(form['year']),
                                           data_verbose(next_form['month']),
                                           data_verbose(next_form['year']),)
                                           
        
    def render(self, context):
        try:
            response = ''
            location_forms = [form for form in self.location_forms.resolve(context).forms]
            for idx, form in enumerate(location_forms, start=1):                
                response += "<tr><td>%d</td><td>%s</td><td>%s</td><td>%s / %s</td></tr>" % (idx,
                                                                                            self.get_time_period(idx, form, location_forms),
                                                                                            (data_verbose(form['state']) if form['state'].data == 'OU' else '%s / %s' % (data_verbose(form['county']), data_verbose(form['state']),)),
                                                                                            data_verbose(form['milksource']), 
                                                                                            data_verbose(form['milkamount']))
            return mark_safe(response)
        except Exception as e:
            print(str(e))
            return ''    
