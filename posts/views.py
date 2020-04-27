from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect(to='index')
        return render(request, 'post_new.html', {'form': form})
    
    form = PostForm()
    return render(request, 'post_new.html', {'form': form})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).order_by('-pub_date')

    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "profile.html", {'author': author, 'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=int(post_id))
    post_count = Post.objects.filter(author=author).count()

    return render(request, "post.html", {'author': author, 'post_count': post_count, 'post': post})


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=int(post_id))

    if request.user != author:
        return redirect(to='post', username=username, post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(to='index')
        return render(request, 'post_new.html', {'form': form, 'edit': True})

    form = PostForm(instance=post)
    return render(request, 'post_new.html', {'form': form, 'edit': True})
