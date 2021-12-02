from django.urls import path
from .views import PostList, PostDetail, CommentList, PostSearch, PostCreateView, PostUpdateView, PostDeleteView, \
    update_me, PostAuthor, PostTag, PostType, ProfileView, subscribe_to_category, unsubscribe_from_category

urlpatterns = [
    path('', PostList.as_view()),  # т. к. сам по себе это класс, то нам надо представить этот класс в виде view.
    # Для этого вызываем метод as_view
    path('news/<int:pk>', PostDetail.as_view()),
    path('comment/', CommentList.as_view()),
    path('search', PostSearch.as_view()),
    path('create', PostCreateView.as_view(), name='post_create'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
    path('edit/<int:pk>', PostUpdateView.as_view(), name='post_edit'),
    path('upgrade/', update_me, name='upgrade'),

    # Urls
    path('author/<int:pk>', PostAuthor.as_view(), name='author_name'),
    path('type/<str:name>', PostType.as_view(), name='post_type'),
    path('tag/<int:pk>', PostTag.as_view(), name='post_tag'),

    path('subscribe/<int:pk>', subscribe_to_category, name='sub_cat'),
    path('unsubscribe/<int:pk>', unsubscribe_from_category, name='unsub_cat'),
    path('profile/', ProfileView.as_view(), name='profile'),
]