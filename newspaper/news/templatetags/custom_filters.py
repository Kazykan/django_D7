from django import template

register = template.Library()  # если мы не зарегистрируем наши фильтры, то Django никогда не узнает,
# где именно их искать и фильтры потеряются

replace_val = [
    ('сук', '***'),
    ('хуй', '***'),
    ('сука', '****'),
    ('Хуй', '***'),
]  # кортеж из слов исключений


@register.filter(name='censor')
def censor(text):
    if isinstance(text, str):  # проверяем, что text — это точно строка
        return replace(text, replace_val)
    else:
        raise ValueError(f'Нужно передвать только текст здесь: {type(text)}')


def replace(text, old_new):  # Замена матов
    for vals in old_new:
        old, new = vals
        text = text.replace(old, new)
    return text


# text = "Привет Cук как дела твари баб хуй вам сук сук сукаб"
# print(replace(text, replace_val))