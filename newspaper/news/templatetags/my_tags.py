from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """Вернуть закодированные параметры URL, которые совпадают с текущими
    параметры запроса, только с добавленными или измененными указанными параметрами GET.

    Он также удаляет все пустые параметры, чтобы все было в порядке,
    так что вы можете удалить параметр, установив для него значение "" "`.

    Например, если вы находитесь на странице `` / things /? With_frosting = true & page = 5``
,
    тогда

    <a href="/things/?{% param_replace page=3 %}"> Стр. 3 </a>

    расширится до

    <a href="/things/?with_frosting=true&page=3"> Стр. 3 </a>
"""
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()
