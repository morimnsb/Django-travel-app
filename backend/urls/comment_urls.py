# backend/urls/comment_urls.py
from django.urls import path
from backend.views.comment_views import add_new_comment, delete_comment, update_comment

urlpatterns = [
    path('add/', add_new_comment, name='add_new_comment'),
    path('delete/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('update/<int:comment_id>/', update_comment, name='update_comment'),
    # Add other URL patterns as needed
]
