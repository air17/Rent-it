from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rentit import settings

urlpatterns = [
    path('', include('rentitapp.urls')),
    path('', include('accounts.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('profile/', include('django.contrib.auth.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
