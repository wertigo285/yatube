from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static

from posts.views import Template404View, Template500View

handler404 = Template404View.get_rendered_view()  # noqa
handler500 = Template500View.get_rendered_view()  # noqa

urlpatterns = [
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('posts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve,
                {'document_root': settings.STATIC_ROOT}),
    ]
