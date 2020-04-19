from django.forms import modelform_factory
from .models import Post


CreationForm = modelform_factory(Post, fields=("text", "group"))
