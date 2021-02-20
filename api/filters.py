from django_filters import rest_framework as filters
from posts.models import Post


class PostFilter(filters.FilterSet):
    group = filters.NumberFilter(field_name='group__id')

    class Meta:
        model = Post
        fields = ['group', ]
