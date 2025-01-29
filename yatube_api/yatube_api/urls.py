from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from api.views import (
    PostsViewSet,
    CommentViewSet,
    GroupViewSet,
    FollowViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

router = SimpleRouter()
router.register('posts', PostsViewSet)
router.register('groups', GroupViewSet)
router.register(r'follow', FollowViewSet,
                basename='follow')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # Добавляем маршруты для Simple JWT
    path('api/v1/jwt/create/', TokenObtainPairView.as_view(),
         name='jwt-create'),
    path('api/v1/jwt/refresh/', TokenRefreshView.as_view(),
         name='jwt-refresh'),
    path('api/v1/jwt/verify/', TokenVerifyView.as_view(),
         name='jwt-verify'),

    path('api/v1/', include(router.urls)),

    path('api/v1/posts/<int:post_id>/comments/',
         CommentViewSet.as_view(
             {
                 'get': 'list',
                 'post': 'create'
             }
         ),
         name='post-comments'),

    path('api/v1/posts/<int:post_id>/comments/<int:id>/',
         CommentViewSet.as_view(
             {
                 'get': 'retrieve',
                 'put': 'update',
                 'patch': 'partial_update',
                 'delete': 'destroy'
             }
         ),
         name='comment-detail'),
]
