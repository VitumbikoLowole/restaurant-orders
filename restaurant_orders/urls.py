from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from menu import auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # login, logout
    path("accounts/register/", auth_views.register, name="register"),
    path("api/", include("menu.api_urls")),
    path("", include("menu.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
