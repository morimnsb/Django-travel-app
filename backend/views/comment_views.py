# backend/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from backend.models import Comment, Post, Reply
from django.forms.models import model_to_dict
import json
from django.core.exceptions import ValidationError
import bcrypt
import jwt
import os

# Add New Comment
@csrf_exempt
@require_POST
def add_new_comment(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        post_id = data.get('postId', '')
        comment_text = data.get('commentText', '')
        writer = data.get('writer', '')

        # Check if Id matches the MongoDB standard
        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({"error": "No such post"}, status=404)

        post = get_object_or_404(Post, id=post_id)

        new_comment = Comment(comment_text=comment_text, writer=writer)
        new_comment.save()

        post.comments.add(new_comment)
        post.save()

        return JsonResponse({"success": True}, status=200)
    except ValidationError as ve:
        return JsonResponse({"error": ve.message}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)

# Delete Comment
@csrf_exempt
def delete_comment(request, id):
    try:
        # Check if Id matches the MongoDB standard
        if not Comment.objects.filter(id=id).exists():
            return JsonResponse({"error": "No such comment"}, status=404)

        comment = get_object_or_404(Comment, id=id)
        comment.delete()

        return JsonResponse({"message": "Comment deleted successfully"})
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)

# Update Comment
@csrf_exempt
def update_comment(request, id):
    try:
        # Check if Id matches the MongoDB standard
        if not Comment.objects.filter(id=id).exists():
            return JsonResponse({"error": "No such comment"}, status=404)

        data = json.loads(request.body.decode('utf-8'))
        reply_text = data.get('replyText', '')
        writer = data.get('writer', '')

        # Update general comment information
        updated_comment = Comment.objects.get(id=id)
        reply = Reply(reply_text=reply_text, writer=writer)
        reply.save()

        updated_comment.replies.add(reply)
        updated_comment.save()

        return JsonResponse({"comment": model_to_dict(updated_comment)}, status=200)
    except ValidationError as ve:
        return JsonResponse({"error": ve.message}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)
