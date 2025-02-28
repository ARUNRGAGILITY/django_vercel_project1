from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

# Ensure static and media directories exist
os.makedirs(settings.STATIC_ROOT, exist_ok=True)
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

urlpatterns = [

    path('admin/', admin.site.urls),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


