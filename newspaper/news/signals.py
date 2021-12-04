from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, PostCategory, CategorySub
from newspaper import config


@receiver(post_save, sender=Post)
def notify_subscribers_publication(instance, created, **kwargs):
    """сигнал на изменения в посте, если пост создан то пропускаем, если пост изменен получаем id всех постов
    через цикл полчаем все email подписчиков на категории и запускаем ф-цию отправки писем"""
    if not created:
        subject = f'Изменена публикация: {instance.headingPost} -- {instance.timeInCreation.strftime("%d %m %Y")}'
        cat_id_list = list(PostCategory.objects.filter(postThrough_id=instance.id).values('categoryThrough_id'))
        list_of_subscribers_all = []

        for cat in cat_id_list:
            cat_id = cat.get('categoryThrough_id')
            filtered_subscribers = list(CategorySub.objects.filter(categorySub_id=cat_id).values('subscriberUser_id__email'))

            list_of_subscribers_to_the_category = add_list_of_subscribers(filtered_subscribers)
            if list_of_subscribers_to_the_category:
                list_of_subscribers_all += list_of_subscribers_to_the_category

        list_of_subscribers_all = list(set(list_of_subscribers_all))  # убираем дубликаты

        if list_of_subscribers_all:
            html = render_to_string('mailings/mailings_create.html', {'form': instance, 'instance': instance.id})
            sending_an_email(subject, html, list_of_subscribers_all)


@receiver(m2m_changed, sender=Post.postCategory.through)
def notify_subscribers_publication(instance, **kwargs):
    """сигнал проверки связей ManyToMany на изменения связей в посте через цикл прогоняем все pk_set записей
     находим через categorySub_id все email добавляем их в список и запускаем ф-цию отправки писем"""
    subject = f'Добавлена публикация: {instance.headingPost} -- {instance.timeInCreation.strftime("%d %m %Y")}'
    list_of_subscribers_all = []

    for cat_id in list(kwargs.get('pk_set')):
        filtered_subscribers = list(CategorySub.objects.filter(categorySub_id=cat_id).values('subscriberUser_id__email'))

        list_of_subscribers_to_the_category = add_list_of_subscribers(filtered_subscribers)
        if list_of_subscribers_to_the_category:
            list_of_subscribers_all += list_of_subscribers_to_the_category

    list_of_subscribers_all = list(set(list_of_subscribers_all))  # убираем дубликаты

    if list_of_subscribers_all:
        html = render_to_string('mailings/mailings_create.html', {'form': instance, 'instance': instance.id})
        sending_an_email(subject, html, list_of_subscribers_all)


def add_list_of_subscribers(filtered_subscribers):
    """из списка удаляем ключь 'subscriberUser_id__email' и оставляем только email
    [{'subscriberUser_id__email': 'email@mail.ru'}, {'subscriberUser_id__email': 'email@mail.com'}]"""
    list_of_subscription_categories = [d['subscriberUser_id__email']
                                       for d in filtered_subscribers if 'subscriberUser_id__email' in d]
    return list_of_subscription_categories


def sending_an_email(subject, html, list_of_subscribers):
    print(f'subject____________________________{subject}')
    print(f'html________________________________{html}')
    print(f'list_of_subscribers_________________{list_of_subscribers}')
    # msg = EmailMultiAlternatives(
    #     subject=subject,
    #     from_email=config.EMAIL_HOST_DJANGO,  # здесь указываете почту, с которой будете отправлять
    #     to=list_of_subscribers,  # здесь список получателей. Например, секретарь, сам врач и т. д.
    # )
    # msg.attach_alternative(html, "text/html")
    # msg.content_subtype = "html"
    # try:
    #     msg.send()
    # except Exception as e:
    #     print(e)


