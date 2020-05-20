from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect


from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related('author').order_by('-pub_date')
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect(to='index')
        return render(request, 'post_new.html', {'form': form})

    return render(request, 'post_new.html', {'form': form})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.select_related('author', 'group').filter(
        group=group).order_by('-pub_date')
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


def profile(request, username):
    profile = get_object_or_404(User.objects
                                .filter(username=username)
                                .annotate(
                                    post_count=Count(
                                        'author_posts', distinct=True),
                                    followers_count=Count(
                                        'following', distinct=True),
                                    following_count=Count(
                                        'follower', distinct=True)
                                ))
    posts = Post.objects.select_related('author', 'group').filter(
        author=profile).order_by('-pub_date')
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=profile).exists()

    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {
        'profile': profile,
        'page': page,
        'paginator': paginator,
        'following': following,
    })


def post_view(request, username, post_id):

    profile = get_object_or_404(User.objects
                                .filter(username=username)
                                .annotate(
                                    post_count=Count(
                                        'author_posts', distinct=True),
                                    followers_count=Count(
                                        'following', distinct=True),
                                    following_count=Count(
                                        'follower', distinct=True)
                                ))
    post = get_object_or_404(Post.objects.select_related(
        'author').filter(author=profile, pk=post_id))
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=profile).exists()

    comment_form = CommentForm()

    comments = Comment.objects.select_related(
        'author').filter(post=post).order_by('-created')

    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'post.html', {
        'profile': profile,
        'post': post,
        'form': comment_form,
        'page': page,
        'paginator': paginator,
        'following': following,
        'comments': comments  # без этой строки не загрузить проект
    })


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, pk=post_id)

    if request.user != author:
        return redirect(to='post', username=username, post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(to='post', username=username, post_id=post_id)
    return render(request, 'post_new.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=profile, pk=post_id)
    if request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.instance.author = request.user
            comment_form.instance.post = post
            comment_form.save()
    return redirect(to='post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related("author", "group").filter(
        author__in=Follow.objects.filter(user=request.user).values('author')).order_by("-pub_date")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect(to='profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()

    return redirect(to='profile', username=username)
