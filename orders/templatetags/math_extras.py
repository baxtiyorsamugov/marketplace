from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Умножает value на arg.
    Пример в шаблоне: {{ a|multiply:b }} => a*b
    """
    try:
        return value * arg
    except Exception:
        return ''
