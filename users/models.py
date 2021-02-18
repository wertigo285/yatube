from django.contrib.auth.models import User


class Profile(User):

    class Meta:
        proxy = True
        ordering = ('first_name', )
