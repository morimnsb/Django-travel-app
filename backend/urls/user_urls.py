# backend/urls/user_urls.py

from django.urls import path
from backend.views.user_views import signup, verify_user, search_user, update_user, sign_in

urlpatterns = [
    path('signup/', signup, name='signup'),
    # path('verify_user/', verify_user, name='verify_user'),
    path('search/<str:username>/', search_user, name='search_user'),
    path('update_user/', update_user, name='update_user'),
    path('signIn/', sign_in, name='signIn'),
    # Add other URL patterns as needed
]
