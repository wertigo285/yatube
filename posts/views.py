from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
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
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(posts, 10) 

    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})

