from django.contrib import admin

from .models import Comment, Follow, Group, Message, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class MessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'dispatched', 'author',)
    search_fields = ('text',)
    list_filter = ('dispatched',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Message, MessageAdmin)
admin.site.register(Follow)
