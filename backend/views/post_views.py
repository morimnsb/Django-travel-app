from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Post, Image
import logging
from django.core.serializers import serialize
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseNotFound  # Add this import
from django.core.exceptions import ObjectDoesNotExist
import json
from django.views.decorators.http import require_http_methods
logger = logging.getLogger(__name__)
# backend/views.py



@csrf_exempt
@require_POST
def add_new_travel(request):
    try:
        # Retrieve data from POST request
        title = request.POST.get('title', '').strip()
        place = request.POST.get('place', '').strip()
        description = request.POST.get('description', '').strip()
        writer = request.POST.get('writer', '').strip()
        writer_id = request.POST.get('writerId', '').strip()
        images = request.POST.getlist('images')
        print("Received images:", images)

        # Get the user instance
        User = get_user_model()
        user = User.objects.get(id=writer_id)

        # Add new travel
        new_travel = Post(
            title=title,
            place=place,
            content='',
            description=description,
            writer=writer,
            writer_id=user,
        )

        new_travel.save()

        # Add image URLs to the new travel
        image_urls = []
        for image_url in images:
            # Create a new Image instance associated with the post
            image_instance = Image.objects.create(post=new_travel, image=image_url)
            print(f"Image saved: {image_instance}")
            image_urls.append(image_instance.image)  # Append the image URL to the list

        user.posts.add(new_travel)

        # Include image URLs in the response
        response_data = {
            "message": "New Travel Added",
            "travel_id": new_travel.id,
            "image_urls": image_urls,
        }
        return JsonResponse(response_data, status=201)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)



@csrf_exempt
def get_all_travels(request):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 5))

        travels = Post.objects.all().order_by('-created_at')[((page - 1) * limit):(page * limit)]

        if travels is not None:
            travels_data = []
            for travel in travels:
                if hasattr(travel, 'id'):
                    images_list = [image.image for image in travel.post_images.all()]
                    # print("images_list",images_list)
                      # Assuming 'post_images_through' is the related name for the PostImage model
                    travel_data = {
                        "id": str(travel.id),
                        "title": travel.title,
                        "place": travel.place,
                        "description": travel.description,
                        "writer": travel.writer,
                        "rating": getattr(travel, 'rating', None),
                        "writerId": str(travel.writer_id),
                        "images": images_list,
                        "created_at": travel.created_at,
                    }
                    travels_data.append(travel_data)

            return JsonResponse({"travels": travels_data})
        else:
            return JsonResponse({"travels": []})

    except Exception as e:
        logger.error("An error occurred during fetching all travels: %s", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)


@csrf_exempt
def get_travel(request, travel_id):
    try:
        travel = get_object_or_404(Post, id=travel_id)

        # Retrieve image URLs using the 'post_images' reverse relation from the 'Post' model
        images_list = [image.image for image in travel.post_images.all()]

        # Include 'ratings' and 'images' in the response
        return JsonResponse({
            "travel": {
                "id": str(travel.id),
                "title": travel.title,
                "place": travel.place,
                "description": travel.description,
                "writer": travel.writer,
                "writerId": str(travel.writer_id),
                "ratings": travel.ratings,
                "images": images_list,
                "created_at": travel.created_at
            }
        })
    except Exception as e:
        logger.error("An error occurred during fetching a travel: %s", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)


from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404

import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.models import User
from backend.models import CustomUser  # Replace with the actual import path for your CustomUser model
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
import json
from django.http import JsonResponse
import json
from django.http import JsonResponse
from rest_framework import serializers

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
@csrf_exempt
@require_http_methods(["POST", "PUT", "PATCH"])

def update_travel(request, travel_id):
    try:
        print("Request received for travel update:", request.body)
        post = Post.objects.get(id=travel_id)

        # Retrieve updated data from the request
        if request.method == 'PATCH':
            data = json.loads(request.body.decode('utf-8'))
            title = data.get('title', '').strip()
            place = data.get('place', '').strip()
            description = data.get('description', '').strip()
            new_images = data.get('images', [])  # Make sure to get new_images from data
    # Add more fields as needed
        else:
            title = request.POST.get('title', '').strip()
            place = request.POST.get('place', '').strip()
            description = request.POST.get('description', '').strip()
            new_images = request.POST.getlist('new_images')
        print(f"Received title: {title}")
        print(f"Received place: {place}")
        print(f"Received description: {description}")
        print(f"Received new_images: {new_images}")
        # Update the post fields
        post.title = title
        post.place = place
        post.description = description
        # Update more fields as needed

        # Save the changes
        post.save()

        # Handle new images
      
        for image_url in new_images:
            # Create a new Image instance associated with the post
            image_instance = Image.objects.create(post=post, image=image_url)
            print(f"New Image saved: {image_instance}")

        return JsonResponse({"message": "Post Updated"}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)


@csrf_exempt
def delete_travel(request, travel_id):
    try:
        travel = get_object_or_404(Post, id=travel_id)
        travel.delete()
        return JsonResponse({"message": "Travel deleted successfully"})
    except Exception as e:
        logger.error("An error occurred during travel deletion: %s", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)

@csrf_exempt
def delete_post_image(request, post_id, filename):
    try:
        post = get_object_or_404(Post, id=post_id)

        image_index = -1
        for i, image_path in enumerate(post.images):
            if filename in image_path:
                image_index = i
                break

        if image_index == -1:
            return JsonResponse({"error": "Image not found"}, status=404)

        image_path = os.path.join('C:/Users/Lucas/Documents/Matrix Master Bootcamp/MERN Projects/travel-app/backend/public/uploads/', filename)
        os.remove(image_path)

        post.images.pop(image_index)
        post.save()

        return JsonResponse({"message": "Image deleted successfully"})
    except Exception as e:
        logger.error("An error occurred during post image deletion: %s", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)

# # views.py
# from django.views.decorators.http import require_http_methods

# @csrf_exempt
# @require_http_methods(["POST", "PUT"])
# def update_travel(request, travel_id):
#     try:
#         post = Post.objects.get(id=travel_id)

#         # Retrieve updated data from the request
#         title = request.POST.get('title', '').strip()
#         place = request.POST.get('place', '').strip()
#         description = request.POST.get('description', '').strip()
#         # Add more fields as needed

#         # Update the post fields
#         post.title = title
#         post.place = place
#         post.description = description
#         # Update more fields as needed

#         # Save the changes
#         post.save()

#         # Handle new images
#         new_images = request.POST.getlist('new_images')
#         for image_url in new_images:
#             # Create a new Image instance associated with the post
#             image_instance = Image.objects.create(post=post, image=image_url)
#             print(f"New Image saved: {image_instance}")

#         return JsonResponse({"message": "Post Updated"}, status=200)
#     except Post.DoesNotExist:
#         return JsonResponse({"error": "Post not found"}, status=404)
#     except Exception as e:
#         print(e)
#         return JsonResponse({"error": "Internal Server Error"}, status=500)
