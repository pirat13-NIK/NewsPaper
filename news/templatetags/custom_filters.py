from django import template
import re

register = template.Library()


@register.filter(name='censor')
def censor(value, forbidden_words):
    """
    Заменяет запрещённые слова: первая и последняя буквы остаются, остальные - звёздочки.
    forbidden_words - список запрещённых слов.
    """
    if not isinstance(value, str):
        return value

    for word in forbidden_words:
        pattern = r'\b' + re.escape(word) + r'\b'

        def replace_match(match):
            matched = match.group()
            if len(matched) <= 2:
                return '*' * len(matched)
            return matched[0] + '*' * (len(matched) - 2) + matched[-1]

        value = re.sub(pattern, replace_match, value, flags=re.IGNORECASE)

    return value