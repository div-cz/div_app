from django import template
import locale

register = template.Library()

@register.filter(name='price')
def price_format(value):
    if value is None:
        return "0"
    try:
        locale.setlocale(locale.LC_ALL, 'cs_CZ.UTF-8')
        return locale.format_string("%.0f", float(value), grouping=True)
    except:
        return str(value)