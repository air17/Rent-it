import debug_toolbar
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rentit import settings

urlpatterns = [
    path('', include('apps.rentitapp.urls')),
    path('profile/', include('apps.accounts.urls')),
    path('profile/', include('django.contrib.auth.urls')),
    path('api/v1/', include('apps.api.urls')),
    path('admin/', admin.site.urls),
    path(r"images-handler/", include("galleryfield.urls")),
    ]

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
