# menas_key/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls')),
    path('dj-admin/', admin.site.urls),  # optional: Django's native admin
]