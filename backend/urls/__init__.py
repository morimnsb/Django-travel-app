# backend/urls/__init__.py

from django.urls import include, path

urlpatterns = [
    path('user/', include('backend.urls.user_urls')),
    path('post/', include('backend.urls.post_urls')),
    path('comment/', include('backend.urls.comment_urls')),
    # Add other URL patterns if needed
]
