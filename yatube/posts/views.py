from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from yatube.settings import NUMBER_PAGINATION_PAGES

from .forms import CommentForm, PostForm, MessageForm
from .models import Comment, Follow, Group, Post, User, Message


def index(request) -> HttpResponse:
    """view-функция для главной страницы."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUMBER_PAGINATION_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page}
    return render(request, 'index.html', context)


def group_posts(request, slug) -> HttpResponse:
    """view-функция для страницы сообщества."""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'posts': posts, 'page': page}
    return render(request, 'group.html', context)


def profile(request, username) -> HttpResponse:
    """view-функция для страницы автора."""
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, NUMBER_PAGINATION_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_anonymous:
        following = False
    else:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    context = {
        'author': author, 'page': page, 'following': following,
    }
    count_posts_and_comments(username, context)
    return render(request, 'posts/profile.html', context)


@login_required
def messages(request, username) -> HttpResponse:
    """view-функция для страницы диалогов."""
    user = get_object_or_404(User, username=username)
    messages_author = Message.objects.filter(author=request.user)
    messages_user = Message.objects.filter(user=request.user)
    messages = messages_author | messages_user
    paginator = Paginator(messages, 50)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = Follow.objects.filter(
            user=request.user, author=user
        ).exists()
    context = {
        'author': user, 'page': page, 'following': following,
    }
    count_posts_and_comments(username, context)
    return render(request, 'posts/messages.html', context)


@login_required
def send_message(request, username) -> HttpResponse:
    """view-функция для отправки сообщения."""
    user = get_object_or_404(User, username=username)
    message = Message(author=request.user, user=user)
    following = Follow.objects.filter(
            user=request.user, author=user
        ).exists()
    form = MessageForm(
        request.POST or None, files=request.FILES or None, instance=message
    )
    if form.is_valid():
        message.save()
        return HttpResponseRedirect(
            reverse('posts:profile', args=(username,))
        )
    context = {
        'author': user, 'message': message, 'form': form,
        'following': following
    }
    count_posts_and_comments(username, context)
    return render(request, 'posts/send_message.html', context)


@login_required
def new_post(request) -> HttpResponse:
    """view-функция для создания нового поста."""
    post = Post(author=request.user)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        post.save()
        return HttpResponseRedirect(reverse('posts:index'))
    context = {'author': request.user, 'post': post, 'form': form}
    count_posts_and_comments(request.user.username, context)
    return render(request, 'posts/post_edit.html', context)


def post_view(request, username, post_id) -> HttpResponse:
    """view-функция для просмотра поста."""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = Comment.objects.filter(post=post)
    paginator = Paginator(comments, NUMBER_PAGINATION_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_anonymous:
        form = CommentForm()
        following = False
    else:
        comment = Comment(author=request.user, post=post)
        form = CommentForm(request.POST or None, instance=comment)
        following = Follow.objects.filter(
            user=request.user, author__username=username
        ).exists()
        if form.is_valid():
            comment.save()
            return HttpResponseRedirect(
                reverse('posts:post', args=(post.author, post.pk))
            )
    context = {
        'author': post.author, 'post': post,
        'form': form, 'page': page, 'following': following,
    }
    count_posts_and_comments(username, context)
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    """view-функция для редактирования поста."""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if request.user != post.author:
        return HttpResponseRedirect(
            reverse('posts:post', args=(post.author, post.pk))
        )
    if form.is_valid():
        post.save()
        return HttpResponseRedirect(
            reverse('posts:post', args=(post.author, post.pk))
        )
    context = {'author': request.user, 'post': post, 'form': form}
    count_posts_and_comments(username, context)
    return render(request, 'posts/post_edit.html', context)


@login_required
def delete_post(request, username, post_id) -> HttpResponse:
    """view-функция для удаления поста"""
    author = get_object_or_404(User, username=username)
    if author == request.user:
        post = get_object_or_404(Post, id=post_id, author__username=username)
        post.delete()
    return HttpResponseRedirect(
        reverse('posts:profile', args=(author,))
    )


@login_required
def delete_comment(request, username, post_id, comment_id) -> HttpResponse:
    """view-функция для удаления комментария"""
    author = get_object_or_404(User, username=username)
    if author == request.user:
        post = get_object_or_404(Post, id=post_id, author__username=username)
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
    return HttpResponseRedirect(
        reverse('posts:post', args=(post.author, post.pk))
    )


@login_required
def follow_index(request):
    """view-функция для просмотра постов текущих подписок."""
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, NUMBER_PAGINATION_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username)


def count_posts_and_comments(username, context):
    """Счётчик постов и комментариев."""
    user = get_object_or_404(User, username=username)
    context['count'] = Post.objects.filter(author=user).count()
    context['count_comment'] = Comment.objects.filter(author=user).count()
    messages_author = Message.objects.filter(author=context['author'])
    messages_user = Message.objects.filter(user=user)
    messages = messages_author | messages_user
    context['messages_count'] = messages.count()
    dialogues_count = list(set(messages.values_list('user', flat=True)))
    context['dialogues_count'] = len(dialogues_count)
    return context


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
