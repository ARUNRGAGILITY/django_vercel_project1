from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os
import importlib

# Ensure static and media directories exist
os.makedirs(settings.STATIC_ROOT, exist_ok=True)
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Dynamically add URLs for `app_` prefixed apps
for app in settings.INSTALLED_APPS:
    if app.startswith("app_"):
        try:
            app_urls = importlib.import_module(f"{app}.app_urls")
            urlpatterns.append(path(f"{app.replace('app_', '')}/", include(f"{app}.app_urls")))
            print(f"✅ Loaded App URLs from: {app}.app_urls")
        except ModuleNotFoundError:
            print(f"❌ No `app_urls.py` found for {app}, skipping.")

# Dynamically add URLs for `rest_` prefixed apps
for app in settings.INSTALLED_APPS:
    if app.startswith("rest_"):
        try:
            rest_urls = importlib.import_module(f"{app}.rest_urls")
            urlpatterns.append(path(f"api/{app.replace('rest_', '')}/", include(f"{app}.rest_urls")))
            print(f"✅ Loaded REST API URLs from: {app}.rest_urls")
        except ModuleNotFoundError:
            print(f"❌ No `rest_urls.py` found for {app}, skipping.")

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# how it will be appended 
# urlpatterns = [
#     path('admin/', admin.site.urls),

#     # Regular Apps
#     path('blog/', include('app_blog.app_urls')),   # ✅ http://127.0.0.1:8000/blog/
#     path('store/', include('app_store.app_urls')), # ✅ http://127.0.0.1:8000/store/

#     # REST APIs (rest_ prefix)
#     path('api/blog/', include('rest_blog.rest_urls')),   # ✅ http://127.0.0.1:8000/api/blog/
#     path('api/store/', include('rest_store.rest_urls')), # ✅ http://127.0.0.1:8000/api/store/
# ]
