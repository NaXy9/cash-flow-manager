from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def rubles(value):
    try:
        amount = Decimal(str(value or 0))
        int_val = int(amount)
        formatted = f"{abs(int_val):,}".replace(",", "\u00a0")
        sign = "−\u202f" if int_val < 0 else ""
        return f"{sign}{formatted}\u202f₽"
    except (InvalidOperation, TypeError, ValueError):
        return "0\u202f₽"


@register.filter
def rubles_signed(value):
    try:
        amount = Decimal(str(value or 0))
        int_val = int(amount)
        formatted = f"{abs(int_val):,}".replace(",", "\u00a0")
        sign = "+\u202f" if int_val >= 0 else "−\u202f"
        return f"{sign}{formatted}\u202f₽"
    except (InvalidOperation, TypeError, ValueError):
        return "0\u202f₽"


@register.simple_tag
def query_transform(request, **kwargs):
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value
    return params.urlencode()
