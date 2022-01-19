from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rentit import settings

urlpatterns = [
    path('', include('rentitapp.urls')),
    path('profile/', include('accounts.urls')),
    path('profile/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path(r"images-handler/", include("galleryfield.urls")),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
