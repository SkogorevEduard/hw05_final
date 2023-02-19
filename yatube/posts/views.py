from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow
from .utils import paginate


def index(request):
    '''View-функция для главной страницы.'''
    post_list = Post.objects.all()
    page_obj = paginate(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''View-функция для страницы, на которой будут посты.'''
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.all()
    page_obj = paginate(request, group_list)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    '''View-функция для страницы, на которой будет профайл пользователя.'''
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginate(request, post_list)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author,
            user=request.user
        ).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''View-функция для просмотра поста.'''
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''View-функция для создания поста.'''
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    '''View-функция для редактирования поста.'''
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    template = 'posts/create_post.html'
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    else:
        return redirect('posts:post_detail', post_id)
    return render(request, template, {'form': form, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    '''View-функция для добавления комментария.'''
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    '''View-функция для страниц избранных авторов.'''
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    '''View-функция для подписки.'''
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    '''View-функция для отписки.'''
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', author)
