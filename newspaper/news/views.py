from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.views.generic.edit import UpdateView
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# права доступа если нет авторизации на сайте
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.urls import resolve
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html

from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from .models import Author, Category, Post, PostCategory, Comment, CategorySub
from .signals import sending_an_email


class PostList(ListView):
    """главная страница с постаринчным выводом"""
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    ordering = ['-timeInCreation']
    paginate_by = 10


class PostDetail(DetailView):
    """отдельный пост"""
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'


class CommentList(ListView):
    model = Comment
    context_object_name = 'comments'
    template_name = 'comments.html'


class PostSearch(ListView):
    """страница с поиском редактирование, добавлением и удалением постов"""
    model = Post
    template_name = 'search.html'
    context_object_name = 'post'
    ordering = ['-timeInCreation']
    paginate_by = 5
    form_class = PostForm  # добавляем форм класс, чтобы получать доступ к форме через метод POST

    def get_filter(self):
        return PostFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, *args, **kwargs):
        context = {
            **super().get_context_data(*args, **kwargs),
            'filter': self.get_filter(),
        }

        context['categories'] = Category.objects.all()
        context['form'] = PostForm()
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        # проверка есть ли пользователь в группе Метод exists() возврашает True если группа authors не найдена
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый пост
            form.save()
        return super().get(request, *args, **kwargs)


class PostCreateView(PermissionRequiredMixin, CreateView):  # доб. параметр если нужно ограничить права
    """добавление поста + разграничение доступа через PermissionRequiredMixin + permission_required """
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('news.add_post', 'news.add_postCategory',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'post_edit.html'
    form_class = PostForm
    permission_required = ('news.change_post', 'news.change_postCategory',)  # редактирование постов

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    """дженерик для удаления постов"""
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/'
    permission_required = ('news.delete_post', 'news.delete_postCategory', )  # удаление постов


class ProfileView(ListView):
    """профиль пользователя со списком его подписок на категории"""
    model = CategorySub
    template_name = 'news/profile.html'
    context_object_name = 'categories'


def page_name(r):
    req = resolve(r.path_info).kwargs['name']
    return req


class PostAuthor(ListView):
    model = Post
    template_name = 'news/subcat/filtered.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        queryset = Post.objects.filter(author=Author.objects.get(id=self.id))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        context['name'] = Author.objects.get(authorUsername=User.objects.get(id=self.id))

        return context


class PostType(ListView):
    model = Post
    template_name = 'news/subcat/filtered.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # self.categoryType = self.get_categoryType_display
        self.name = resolve(self.request.path_info).kwargs['name']
        queryset = Post.objects.filter(categoryType=self.name)
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        # context['data'] = page_name(self.request)
        context['name'] = self.name

        return context


class PostTag(ListView):
    """страница с тегами и возможностью подписаться на них"""
    model = Post
    template_name = 'news/subcat/filtered.html'
    context_object_name = 'news'
    paginate_by = 10
    ordering = ['-timeInCreation']

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        queryset = Post.objects.filter(postCategory=Category.objects.get(id=self.id))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        context['name'] = Category.objects.get(id=self.id)

        return context


@login_required
def update_me(request):
    """добавления пользователя в группу авторы с проверкой является ли он автором"""
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')


@login_required
def subscribe_to_category(request, pk):
    """Подписка пользователя в категорию новостей, проверка есть ли он там
    и если нет добавление с отравкой письма, что он подписан"""
    user = request.user
    category_subscribe = Category.objects.get(id=pk)

    if not category_subscribe.subscribers.filter(id=user.id).exists():
        category_subscribe.subscribers.add(user)
        html = render_to_string('news/subcat/subscribers.html', {'categories': category_subscribe, 'user': user})
        subject = f'Вы подписались на категорию: {category_subscribe}'
        list_of_subscribers = list(user.email)[0]  # преобразуем в список с одним значением
        sending_an_email(subject, html, list_of_subscribers)  # отпраляем письмо
        return redirect('/news/profile/')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unsubscribe_from_category(request, pk):
    """Отписка пользователя от категории, с проверкой есть он там или нет"""
    user = request.user
    category_unsubscribe = Category.objects.get(id=pk)

    if category_unsubscribe.subscribers.filter(id=user.id).exists():
        category_unsubscribe.subscribers.remove(user)
    return redirect('/profile/')


