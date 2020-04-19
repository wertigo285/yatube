from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import CreationForm
from datetime import datetime


def index(request):
    latest = Post.objects.order_by('-pub_date')[:11]
    return render(request, 'index.html', {'posts': latest})


@login_required
def new_post(request):
    if request.method == 'POST':
        new_post = Post(pub_date=datetime.now(), author=request.user)
        form = CreationForm(request.POST, instance=new_post)
        if form.is_valid():
            form.save()
            return redirect(to='index')
    else:
        form = CreationForm()
    return render(request, 'new.html', {'form': form})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by('-pub_date')[:12]
    return render(request, 'group.html', {'group': group, 'posts': posts})
