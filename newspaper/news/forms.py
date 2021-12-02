from django.forms import ModelForm, TextInput, Textarea, Select, NumberInput, FileInput
from .models import Post


class PostForm(ModelForm):
# в класс мета, как обычно, надо написать модель, по которой будет строится форма и нужные нам поля.
# Мы уже делали что-то похожее с фильтрами.
    class Meta:
        model = Post
        fields = [
            'choicePost',
            'headingPost',
            'textPost',
            'author',
            'photo',
            'postCategory',
        ]

        # widgets = {
        #     'choicePost': Select(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Тип поста'
        #     }),
        #     'headingPost':TextInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Заголовок'
        #     }),
        #     'textPost': Textarea(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Содержание'
        #     }),
        #     'ratingPost': NumberInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Содержание'
        #     }),
        #     'author': Select(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Автор'
        #     }),
        #     'photo': FileInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Фото'
        #     }),
        # }
