from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post
from datetime import timedelta, date

# from django.utils.timezone import datetime, timedelta, timezone, timestamp


def get_email_list_subscribers(category):
    """получаем почтовый список юзеров подписанных на категории"""
    user_emails = []
    for user in category.subscribers.all():
        user_emails.append(user.email)
    return user_emails


def send_emails(post_object, *args, **kwargs):
    """отправка почты"""
    html = render_to_string(
        kwargs['template'],
        {'category_object': kwargs['category_object'], 'post_object': post_object},
    )
    """временно отключаем отпраку писем для теста"""
    print(html)
    print(kwargs['email_subject'])
    print(kwargs['user_emails'])
    # msg = EmailMultiAlternatives(
    #     subject=kwargs['email_subject'],
    #     from_email='email@yandex.ru',
    #     to=kwargs['user_emails']  # отправляем всем из списка
    # )
    # msg.attach_alternative(html, 'text/html')
    # msg.send()


def new_post_subscription(instance):

    # latest_post = Post.objects.all().order_by('-dateCreated')[0]
    template = 'news/subcat/newpost.html'
    latest_post = instance

    if not latest_post.isUpdated:
        for category in latest_post.postCategory.all():
            email_subject = f'New post in category: "{category}"'
            user_emails = get_email_list_subscribers(category)
            send_emails(
                latest_post,
                category_object=category,
                email_subject=email_subject,
                template=template,
                user_emails=user_emails)


def notify_subscribers_weekly():
    week = timedelta(days=7)
    posts = Post.objects.all()
    past_week_posts = []
    template = 'news/subcat/weekly_digest.html'
    email_subject = 'Weekly digest for subscribed categories'

    for post in posts:
        """ищем свежие новости, меньше timedelta добавляем их в список"""
        time_delta = date.today() - post.timeInCreation.date()
        if time_delta < week:
            past_week_posts.append(post)

    past_week_categories = set()
    for post in past_week_posts:
        """получаем категории всех постов добавляем их в past_week_categories"""
        for category in post.postCategory.all():
            past_week_categories.add(category)
            # print(post.postCategory.all().filter(catsub=category))

    print(past_week_categories)

    user_emails = set()
    for category in past_week_categories:
        """категории постов передаев ф-ции get_email_list_subscribers и
        полчаем список почтовых адресов"""
        # # print(category.subscribers.all())
        # email_subject = f'New post in category: "{category}"'
        get_user_emails = (set(get_email_list_subscribers(category)))
        user_emails.update(get_user_emails)
        print(get_user_emails)

    # print(post.postCategory.all().filter(postCategory=category))
    # print(user_emails)

    for user_email in user_emails:
        post_object = []
        category_set = set()

        for post in past_week_posts:
            subscription = post.postCategory.all().values('subscribers').filter(subscribers__email=user_email)
            print(subscription)

            if subscription.exists():
                # print(subscription)
                post_object.append(post)
                category_set.update(post.postCategory.filter(subscribers__email=user_email))
        print(user_email)
        print(post_object)
        category_object = list(category_set)
        print(category_object)
        print(set(post.postCategory.all()))

        # send_emails(
        #     post_object,
        #     category_object=category_object,
        #     email_subject=email_subject,
        #     template=template,
        #     user_emails=[user_email, ])

