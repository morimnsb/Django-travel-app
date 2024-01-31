# urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('backend.urls.user_urls')),  # Include the user URLs under 'user/'
    path('post/', include('backend.urls.post_urls')),  # Include the post URLs under 'post/'
    # Add other URL patterns as needed
]
