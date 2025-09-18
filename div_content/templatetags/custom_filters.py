from django import template
import locale

register = template.Library()

@register.filter(name='price')
def price_format(value):
    if value is None:
        return "0"
    try:
        # locale.setlocale(locale.LC_ALL, 'cs_CZ.UTF-8')
        return locale.format_string("%.0f", float(value), grouping=True)
    except:
        return str(value)


@register.filter(name="div_split")
def div_split(value, delimiter=","):
    """
    Rozdělí string podle delimiteru a vrátí list.
    Bezpečně vrací [] když je hodnota None nebo prázdná.
    Použití:
        {{ "A,B,C"|div_split:"," }}
    """
    if value:
        return value.split(delimiter)
    return []

@register.filter(name="div_get")
def div_get(value, index):
    """
    Vrátí bezpečně položku seznamu podle indexu.
    Pokud index neexistuje, vrátí prázdný string.
    Použití:
        {{ some_list|div_get:0 }}
    """
    try:
        return value[int(index)]
    except (IndexError, ValueError, TypeError):
        return ""