from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls import handler404, handler500

from posts.views import Error404View, Error500View

handler404 = Error404View.get_rendered_view()  # noqa
handler500 = Error500View.get_rendered_view()  # noqa

urlpatterns = [
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('posts.urls')),
]
