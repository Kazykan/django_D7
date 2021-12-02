from django.contrib import admin
from .models import Post, Author, PostCategory, Category, CategorySub, Comment


class CategoryInline(admin.TabularInline):
    model = Post.postCategory.through


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'choicePost', 'headingPost', 'preview', 'ratingPost', 'timeInCreation', 'author')
    list_display_links = ('id', 'headingPost')
    search_fields = ('headingPost', 'author',)
    exclude = ('postCategory', )
    inlines = (
        CategoryInline,
    )


admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Author)
admin.site.register(PostCategory)
admin.site.register(CategorySub)
admin.site.register(Comment)
