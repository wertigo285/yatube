from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', max_length=50, unique=True)
    description = models.TextField('description')

    def __str__(self):
        return f'/{self.slug}/{self.title}'


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        'date published', auto_now_add=True, db_index=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author_posts')
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='group_posts'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return f'Post {self.pk}/{self.author}/{self.pub_date}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author_comments')
    text = models.TextField()
    created = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Comment {self.pk}/{self.author}/{self.created} \
            for {self.post}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_following')
        ]

    def __str__(self):
        return f'follow {self.user} - {self.author}'
