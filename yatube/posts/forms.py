from django.forms import ModelForm

from .models import Comment, Post, Message


class PostForm(ModelForm):
    """Форма для постов."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)


class CommentForm(ModelForm):
    """Форма для комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)    


class MessageForm(ModelForm):
    """Форма для сообщений."""

    class Meta:
        model = Message
        fields = ('text', 'image',)
