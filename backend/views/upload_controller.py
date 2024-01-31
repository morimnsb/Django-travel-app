# # backend/views/upload_controller.py

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST, require_GET
# from django.views.decorators import api_view
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _

# from .upload_utils import
# #  upload_image, 
#  get_image_paths, download_image

# @csrf_exempt
# @require_POST
# @api_view(['POST'])
# def upload_image_view(request):
#     if 'image' not in request.FILES:
#         raise ValidationError(_("No image file provided"))

#     image_files = request.FILES.getlist('image')
#     try:
#         image_paths = upload_image(image_files)
#         return JsonResponse({'image_paths': image_paths}, status=200)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# @require_GET
# @api_view(['GET'])
# def get_image_paths_view(request):
#     try:
#         image_paths = get_image_paths()
#         return JsonResponse({'image_paths': image_paths}, status=200)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# @require_GET
# @api_view(['GET'])
# def download_image_view(request):
#     if 'image_url' not in request.query_params:
#         return JsonResponse({'error': 'Image URL not provided'}, status=400)

#     image_url = request.query_params['image_url']
#     try:
#         downloaded_image_url = download_image(image_url)
#         return JsonResponse({'downloaded_image_url': downloaded_image_url}, status=200)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
