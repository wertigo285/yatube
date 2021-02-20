from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, \
                                            TokenRefreshView

from .views import PostViewset, CommentViewset, FolowViewset, GroupViewset

router = DefaultRouter()
router.register('posts', PostViewset)
router.register(
    'posts/(?P<post_id>[^/.]+)/comments', CommentViewset, basename='comment')
router.register('follow', FolowViewset)
router.register('group', GroupViewset)

urlpatterns = [
    path('v1/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('v1/', include(router.urls)),
]
