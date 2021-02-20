from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter


from posts.models import Post, Follow, Group
from .serializers import PostSerializer, CommentSerializer, \
    FollowSerializer, GroupSerializer
from .permissions import IsAuthorOrReadOnly
from .filters import PostFilter


class PostViewset(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PostFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewset(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly, ]

    def get_queryset(self):
        post = get_object_or_404(
            Post.objects.prefetch_related('comments'),
            id=self.kwargs['post_id']
        )
        return post.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FolowViewset(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthorOrReadOnly, ]
    filter_backends = [SearchFilter]
    search_fields = ['=author__username', '=user__username']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GroupViewset(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
