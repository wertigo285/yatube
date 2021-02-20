from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, FormMixin, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


from .models import Comment, Follow, Group, Post, User
from .forms import CommentForm, PostForm


class PostList(ListView):
    model = Post
    queryset = Post.objects.select_related('author', 'group').annotate(
        comment_count=Count('comments', distinct=True)
    )
    template_name = 'index.html'
    paginate_by = 10


class FollowList(LoginRequiredMixin, PostList):
    template_name = 'follow.html'

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(author__in=Follow.objects.filter(
            user=user).values('author'))


class GroupView(SingleObjectMixin, PostList):
    template_name = 'group.html'
    queryset = PostList.queryset

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Group.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(group=self.object)


class PostMixin:
    model = Post
    form_class = PostForm


class CreatePost(PostMixin, LoginRequiredMixin, CreateView):
    template_name = 'post_new.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdate(PostMixin, LoginRequiredMixin, UpdateView):
    template_name = 'post_new.html'
    slug_field = 'author__username'
    slug_url_kwarg = 'username'
    pk_url_kwarg = 'post_id'
    query_pk_and_slug = True

    def get_object(self, *args, **kwargs):
        user = self.request.user
        return super().get_object(
            queryset=self.get_queryset().filter(author=user))

    def get_success_url(self):
        return reverse_lazy('post', kwargs=self.kwargs)


class ProfileMixin(SingleObjectMixin):
    template_name = 'profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    ordering = '-pub_date'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=User.objects.annotate(
            post_count=Count(
                'author_posts', distinct=True),
            followers_count=Count(
                'following', distinct=True),
            following_count=Count(
                'follower', distinct=True)
        ).all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        following = False
        if self.request.user.is_authenticated:
            following = Follow.objects.filter(
                user=self.request.user, author=self.object).exists()
        context['following'] = following

        return context


class ProfileView(ProfileMixin, PostList):

    queryset = PostList.queryset

    def get_queryset(self):
        return self.queryset.filter(author=self.object)


class PostView(ProfileMixin, FormMixin, ListView):
    template_name = 'post.html'
    form_class = CommentForm
    ordering = '-created'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post

        return context

    def get_queryset(self):
        self.post = get_object_or_404(
            Post, author=self.object, pk=self.kwargs['post_id'])
        return self.post.comments.select_related('author')


class CommentCreate(LoginRequiredMixin, CreateView):
    http_method_names = ['post']
    model = Comment
    fields = ['text']

    def form_valid(self, form):
        post = get_object_or_404(
            Post, author__username=self.kwargs['username'],
            pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post', kwargs=self.kwargs)


class FollowView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('profile', kwargs=self.kwargs)

    def _is_author(self, request, **kwargs):
        self.author = get_object_or_404(User, **kwargs)
        user = request.user
        return user == self.author if not user.is_anonymous else True


class FollowCreate(FollowView):

    def get(self, request, *args, **kwargs):
        if not self._is_author(request, **kwargs):
            Follow.objects.get_or_create(user=request.user, author=self.author)
        return super().get(request, *args, **kwargs)


class FollowDelete(FollowView):

    def get(self, request, *args, **kwargs):
        if not self._is_author(request, **kwargs):
            Follow.objects.filter(
                user=request.user, author=self.author).delete()
        return super().get(request, *args, **kwargs)


class ErrorView(TemplateView):
    code = 0

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = self.code
        return response

    @classmethod
    def get_rendered_view(cls):
        as_view_fn = cls.as_view()

        def view_fn(request, *args, **kwargs):
            response = as_view_fn(request)
            response.render()
            return response

        return view_fn


class Error404View(ErrorView):
    template_name = "misc/404.html"
    code = 404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['path'] = self.request.path
        return context


class Error500View(ErrorView):
    template_name = "misc/500.html"
    code = 500
