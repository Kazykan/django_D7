import django_filters  # импортируем filterset, чем-то напоминающий знакомые дженерики
from .models import Post


class PostFilter(django_filters.FilterSet):
    time = django_filters.DateTimeFromToRangeFilter(field_name='timeInCreation', label='Время')
    # time = django_filters.DateTimeFromToRangeFilter(lookup_expr='icontains',
    #                                                 widget=RangeWidget(attrs={'type': 'datetime-local'}),
    #                                                 field_name='timeInCreation')
    heading = django_filters.CharFilter(field_name='headingPost', lookup_expr='icontains', label='Заголовок')
    author = django_filters.CharFilter(field_name='author__authorUser__username',
                                       lookup_expr='icontains', label='Автор')

    class Meta:
        model = Post
        fields = ['time', 'heading', 'author']
        # fields = {
        #     'timeInCreation': ['gt'],  # gt больше, lt меньше  Позже какой-либо даты
        #     'headingPost': ['icontains'],  # приблизительный поиск
        #     'author__authorUser__username': ['icontains']  # Автор
        # }