# backend/urls/post_urls.py
from django.urls import path
from backend.views.post_views import get_all_travels, add_new_travel, get_travel, update_travel, delete_travel, delete_post_image

urlpatterns = [
    path('all/', get_all_travels, name='get_all_travels'),
    path('add_new_travel/', add_new_travel, name='add_new_travel'), 
    path('<int:travel_id>/', get_travel, name='get_travel'),
    path('update/<int:travel_id>/', update_travel, name='update_travel'),
    path('delete/<int:travel_id>/', delete_travel, name='delete_travel'),
    path('delete-image/<int:image_id>/', delete_post_image, name='delete_post_image'),
    # Add other URL patterns as needed
]
