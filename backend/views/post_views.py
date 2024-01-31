from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Post, Image
import logging
from django.core.serializers import serialize
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)

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
        if images:
            for image_url in images:
                # Create a new Image instance associated with the post
                image_instance = Image.objects.create(post=new_travel, image=image_url)

        # Push only the post ID to the user's posts array
        user.posts.add(new_travel)

        return JsonResponse({"message": "New Travel Added", "travel_id": new_travel.id}, status=201)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)

@csrf_exempt
@require_GET
def get_all_travels(request):
    try:
        travels = Post.objects.all()
        serialized_travels = serialize('json', travels)
        return JsonResponse({"travels": serialized_travels})
    except Exception as e:
        logger.error("An error occurred during fetching all travels: %s", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)

# @csrf_exempt
# def get_all_travels(request):
#     try:
#         page = int(request.GET.get('page', 1))
#         limit = int(request.GET.get('limit', 5))

#         travels = Post.objects.all().order_by('-created_at')[((page - 1) * limit):(page * limit)]

#         if travels is not None:
#             travels_data = [
#                 {
#                     "id": str(travel.id),
#                     "title": travel.title,
#                     "place": travel.place,
#                     "description": travel.description,
#                     "writer": travel.writer,
#                     "rating": getattr(travel, 'rating', None),  # Ensure rating is available
#                     "writerId": str(travel.writer_id),
#                     "images": travel.images,
#                     "created_at": travel.created_at,
#                 }
#                 for travel in travels if hasattr(travel, 'id')  # Check if 'id' attribute exists
#             ]
#             return JsonResponse({"travels": travels_data})
#         else:
#             return JsonResponse({"travels": []})

#     except Exception as e:
#         logger.error("An error occurred during fetching all travels: %s", e)
#         return JsonResponse({"error": "Internal Server Error"}, status=500)

@csrf_exempt
def get_travel(request, id):
    try:
        travel = get_object_or_404(Post, id=id)
        return JsonResponse({"travel": {"id": str(travel.id), "title": travel.title, "place": travel.place,
                                        "description": travel.description, "writer": travel.writer,
                                        "rating": travel.rating, "writerId": str(travel.writer_id),
                                        "images": travel.images, "created_at": travel.created_at}})
    except Exception as e:
        logger.error("An error occurred during fetching a travel: %s", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)

@csrf_exempt
@require_POST
def update_travel(request, travel_id):
    try:
        if not travel_id.isnumeric():
            return JsonResponse({"error": "No such travel post"}, status=404)

        travel = get_object_or_404(Post, pk=travel_id)

        # Check if the user making the request is the owner of the travel post
        if request.user != travel.writer:
            return JsonResponse({"error": "Unauthorized access"}, status=403)

        # Update the travel post data
        travel.title = request.POST.get('title', travel.title)
        travel.description = request.POST.get('description', travel.description)
        travel.place = request.POST.get('place', travel.place)  # Corrected assignment from location to place

        # Save the updated travel post to the database
        travel.save()

        return JsonResponse({"message": "Travel post updated successfully"})
    except Exception as e:
        logger.error("An error occurred during travel post update: %s", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)


@csrf_exempt
def delete_travel(request, id):
    try:
        travel = get_object_or_404(Post, id=id)
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
