from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView

from posts.views import Error404View, Error500View

handler404 = Error404View.get_rendered_view()  # noqa
handler500 = Error500View.get_rendered_view()  # noqa

urlpatterns = [
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('redoc/', TemplateView.as_view(template_name='redoc.html'),
         name='redoc'),
    path('', include('posts.urls')),
]
