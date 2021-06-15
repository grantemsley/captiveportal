from django import template
from django.utils.safestring import mark_safe
register = template.Library()


@register.simple_tag(takes_context=True)
def voucher(context, template, code, loopcounter):
    template = template.replace("#PORTALNAME#", context['portal'].name)
    template = template.replace("#SSID#", context['portal'].ssid)
    template = template.replace("#PSK#", context['portal'].psk)
    template = template.replace("#CODE#", code)
    template = template.replace("#TIMELIMIT#", context['roll'].time_limit)
    template = template.replace("#ROLLNUMBER#", str(context['roll'].number))
    template = template.replace("#ROLLDESCRIPTION#", context['roll'].description)
    template = template.replace("#LOOPCOUNTER#", str(loopcounter))
    
    return mark_safe(template)
