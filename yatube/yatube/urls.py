from django.conf import settings
from django.conf.urls import handler404, handler500, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


handler404 = 'posts.views.page_not_found'
handler500 = 'posts.views.server_error'

urlpatterns = [
    path('about/', include('about.urls', namespace='about')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('captcha/', include('captcha.urls')),
    path('api/', include('api.urls', namespace='api-v1')),
]

schema_view = get_schema_view(
    openapi.Info(
        title="EVER API",
        default_version='v1',
        description="Документация для сети EVER",
        # terms_of_service="URL страницы с пользовательским соглашением",
        contact=openapi.Contact(email="ura.yakovlev@yandex.ru"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'),
]

urlpatterns += [
    path('', include('posts.urls', namespace='posts')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
