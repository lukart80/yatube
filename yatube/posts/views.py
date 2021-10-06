from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def paginator_page(request, objects, items_per_page, paginator_class):
    """Функция для возвращения страницы Пагинатора."""
    paginator = paginator_class(objects, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page


@cache_page(20, key_prefix='index_page')
def index(request):
    """View функция для главной страницы."""
    post_list = Post.objects.select_related('group').all()
    page = paginator_page(
        request, post_list, settings.ITEMS_PER_PAGE, Paginator)
    return render(request, 'index.html', {'page': page, })


def group_posts(request, slug):
    """View функция для страницы сообществ."""
    group = get_object_or_404(Group, slug=slug)
    posts_list = Post.objects.filter(group=group)
    page = paginator_page(
        request, posts_list, settings.ITEMS_PER_PAGE, Paginator)
    context = {
        'group': group,
        'page': page,

    }
    return render(request, 'group.html', context)


def profile(request, username):
    """View функция для просмотра профиля автора."""
    author = User.objects.prefetch_related('posts').get(username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'author': author,
        'page': page,
        'posts': posts
    }
    if request.user.is_authenticated:
        author = get_object_or_404(User, username=username)
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
        context['following'] = following
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    """View функция для просмотра поста."""
    author = User.objects.prefetch_related('posts').get(username=username)
    post = author.posts.get(id=post_id)
    form = CommentForm()
    context = {
        'author': author,
        'post': post,
        'form': form,
    }
    return render(request, 'post.html', context)


@login_required
def new_post(request):
    """View функция для создания поста."""
    form = PostForm(request.POST or None, request.FILES or None)
    context = {'form': form}
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            return redirect('index')
        return render(request, 'new_post.html', context)
    return render(request, 'new_post.html', context)


@login_required
def post_edit(request, username, post_id):
    """View функция для редактирования поста."""
    if request.user.username == username:
        TYPE = 'edit'
        post = Post.objects.get(pk=post_id)
        form = PostForm(request.POST or None,
                        instance=post,
                        files=request.FILES or None)
        context = {
            'type': TYPE,
            'form': form,
            'post': post,
        }
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('post', username, post_id)
            return render(request, 'new_post.html', context)
        return render(request, 'new_post.html', context)
    return redirect('post', username, post_id)


def page_not_found(request, exception):
    """View-функция для отображение страницы ощибки 404."""
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    """View-функция для отображение страницы ошибки 500."""
    return render(request, "misc/500.html", status=500)


@require_POST
@login_required
def add_comment(request, username, post_id):
    form = CommentForm(data=request.POST)
    if form.is_valid():
        post = get_object_or_404(Post, id=post_id)
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username, post_id)
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    """View-функция для просмотра постов авторов, на которых подписан."""
    posts = Post.objects.filter(author__following__user=request.user)
    page = paginator_page(
        request, posts, settings.ITEMS_PER_PAGE, Paginator)
    context = {'page': page}
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)

    if request.user.username == username:
        return redirect('profile', username)

    try:
        Follow.objects.create(
            user=request.user,
            author=author
        )
    except IntegrityError:
        return redirect('profile', username)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect('profile', username)
