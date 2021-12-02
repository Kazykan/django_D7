from django.contrib.auth.models import User, Group
from django.db import models
from datetime import datetime
from django.db.models import Sum
from django.urls import reverse # работа со ссылками
from allauth.account.forms import SignupForm


class Author(models.Model):
    """Авторы статей"""
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    ratingAuthor = models.SmallIntegerField(default=0, verbose_name='Рейтинг')
    avatar = models.ImageField(upload_to='photo/img_avatar', blank=True, null=True, verbose_name='Фото')

    def update_rating(self):
        postRat = self.post_set.all().aggregate(postRating=Sum('ratingPost'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.all().aggregate(commentRating=Sum('ratingComment'))
        cRat = 0
        cRat += commentRat.get('commentRating')

        self.ratingAuthor = pRat * 3 + cRat
        self.save()

    def __str__(self):
        return f'{self.authorUser.username} {self.authorUser.first_name}'

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-authorUser']  # Сортировка по имени


class Category(models.Model):
    """категории постов + подписчики на эту категорию"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Категория')
    subscribers = models.ManyToManyField(
        User,
        through='CategorySub',
        blank=True,
        verbose_name='Подписчики')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['-name']  # Сортировка по имени


class Post(models.Model):
    """Статьи/новости"""
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья')
    )

    choicePost = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        default=NEWS,
        verbose_name='Тип поста')  # поле с выбором — «статья» или «новость»
    headingPost = models.CharField(max_length=128, verbose_name='Заголовок')
    textPost = models.TextField(verbose_name='Содержание')
    ratingPost = models.SmallIntegerField(default=0, verbose_name='Рейтинг')
    timeInCreation = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    photo = models.ImageField(upload_to='photo/%Y/%m/%d/', blank=True, null=True, verbose_name='Фото')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    postCategory = models.ManyToManyField(Category, through='PostCategory', verbose_name='Категории')

    class Meta:
        verbose_name = "Пост/новость"
        verbose_name_plural = "Посты/новости"

    def preview(self):
        return self.textPost[0:123]+'...'

    def like(self):
        self.ratingPost += 1
        self.save()

    def dislike(self):
        self.ratingPost -= 1
        self.save()

    def __str__(self):
        return f'{self.headingPost.title()}: {self.textPost[:60]}'

    def get_absolute_url(self):
        return f'/news/{self.id}'


class PostCategory(models.Model):
    """категирия постов"""
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост/новость')
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    def __str__(self):
        return f'{self.postThrough.headingPost[:20]}: {self.categoryThrough.name}'

    class Meta:
        verbose_name = "Категория статьи/новости"
        verbose_name_plural = "Категории статей/новостей"


class CategorySub(models.Model):
    """Подписчик на категорию"""
    categorySub = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True,  verbose_name='Категория')
    subscriberUser = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Подписчик')

    def __str__(self):
        return f'{self.subscriberUser.username} подписан на: {self.categorySub.name}'

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def get_category_sub(self):
        return self.categorySub.name

    def get_subscriber_user(self):
        return self.subscriberUser.name


class Comment(models.Model):
    """комментарии к статьям/новостям + рейтинги этих комментариев"""
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timeInCreation = models.DateTimeField(auto_now_add=True)  # Автоматическое добавление даты создания комментария
    ratingComment = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.commentUser.username} {self.commentUser.first_name} {self.commentPost.headingPost[:20]}'

    def like(self):
        self.ratingComment += 1
        self.save()

    def dislike(self):
        self.ratingComment -= 1
        self.save()


class CommonSignupForm(SignupForm):
    """форма для добавления в группу common при регистрации через allauth"""

    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user
