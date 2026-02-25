from django import template
import re

register = template.Library()

CENSORED_WORDS = ['редиска', 'нехорошее слово', 'плохое слово', 'ругательство']


@register.filter(name='censor')
def censor(value):
    if not isinstance(value, str):
        return value

    for word in CENSORED_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'

        value = re.sub(pattern, lambda m: '*' * len(m.group()), value, flags=re.IGNORECASE)

    return value