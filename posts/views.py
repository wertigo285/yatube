from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import PostForm


def index(request):
    latest = Post.objects.order_by('-pub_date')[:11]
    return render(request, 'index.html', {'posts': latest})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect(to='index')
        else:
            #Если валидация формы не пройдет(предположим добавится валидатор)
            #и я уберу этот else 
            #пользовтель получит пустую форму, без пояснений и без
            #введенных ранее данных, так должно работать?
            #Или перенести создание пустой формы выше проверки на тип запроса
            #и 2 раза объект формы создавать при post? Так разве лучше будет?
            return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by('-pub_date')[:12]
    return render(request, 'group.html', {'group': group, 'posts': posts})
