from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', max_length=50, unique=True)
    description = models.TextField('description')

    def __str__(self):
        return '/' + self.slug + '/ ' + self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author_posts')
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, blank=True, null=True, related_name='group_posts')
