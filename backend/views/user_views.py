# backend/views/user_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
import json
from django.shortcuts import render
from django.contrib.auth import get_user_model 
from django.contrib.auth.models import User
import bcrypt
import jwt
import os
import logging
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.core.validators import validate_email
from django.core.serializers import serialize
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.password_validation import validate_password
from backend.models import CustomUser
# from .upload_image import upload_image  # Assuming you have an 'upload_image' function in the same directory

# Configure logging
logger = logging.getLogger(__name__)
User = get_user_model() 


@csrf_exempt
@require_POST
def signup(request):
  
    # if request.method == 'POST':
    #     # Your signup logic here
    #     return JsonResponse({'message': 'Signup successful'}, status=201)
    # else:
    #     return JsonResponse({'message': 'Invalid request method'}, status=400)

    try:
        print("Request Data:", request.body)
        data = validate_signup_request(request)
        print("Validated Data:", data)

        # Check if the email already exists
        if CustomUser.objects.filter(email=data['email']).exists():
            raise ValidationError("Email is already in use")

        # Validate email format
        email = data['email']
        if not email:
            raise ValidationError("Email is required")
        validate_email(email)

        # Validate password complexity
        validate_password(data['password'])

        # Hash the user's password using bcrypt with a salt factor of 12
        hashed_pass = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt(12))

        # Create a new user object with hashed password
        new_user = CustomUser(
            username=data['userName'],
            email=data['email'],
            password=hashed_pass.decode('utf-8'),
        )

        # Save the new user to the database
        new_user.save()

        # Send a success response if the user is saved successfully
        return JsonResponse({"message": "User saved successfully"})
    except (ValidationError, password_validation.ValidationError) as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        print("Error:", e)
        logger.error("An error occurred during user signup: %s", e)
        return JsonResponse({"error": "An error occurred while saving the user."}, status=500)


# Function for user signIn
@csrf_exempt
@require_POST
def sign_in(request):
    try:
        print("Request Data:", request.body)
        data = validate_sign_in_request(request)
        print("Validated Data:", data)

        # Parse JSON data from the request body
        email = data.get('email')
        password = data.get('password')

        # Check if the user with the provided email exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return JsonResponse(error_response("User not found"), status=404)

        # Print user information for debugging
        print("User Information:", {
            "username": user.username,
            "email": user.email,
            "password": user.password,
           
        })

        # Compare the hashed password
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Authentication successful
            login(request, user)
            
            # Include additional user information in the response
            response_data = {
                "message": "User signed in successfully",
                "username": user.username,
                "email": user.email,
                 "user_id": user.id
            }
            
            return JsonResponse(success_response(response_data))
        else:
            # Print additional information for failed authentication
            print("Authentication failed. Password hash does not match.")
            return JsonResponse(error_response("Invalid credentials"), status=401)

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format in request body"}, status=400)
    except Exception as e:
        print("Error:", e)
        return JsonResponse({"error": "An error occurred during sign-in"}, status=500)







# Function to verify user token
def verify_user(request):
    try:
        token = request.headers['Authorization']
        decoded = jwt.decode(token.replace("Bearer ", ""), os.environ.get("SECRET"), algorithms=["HS256"])

        return JsonResponse(success_response({
            "userId": decoded['id'],
            "username": decoded['userName'],
            "avatar": decoded['avatar'],
        }))
    except jwt.ExpiredSignatureError:
        return JsonResponse(error_response("Token has expired"), status=401)
    except jwt.InvalidTokenError:
        return JsonResponse(error_response("Invalid token"), status=401)

# Function to search for a user by username
def search_user(request, username):
    try:
        user = get_object_or_404(User, username=username)
        user_info = {
            "id": str(user.id),
            "userName": user.username,
            "email": user.email,
            "posts": serialize('json', user.posts.all()), 
            # "avatar": str(user.avatar),
        }
        return JsonResponse(success_response({"userInfo": user_info}))
    except Exception as e:
        logger.error("An error occurred during user search: %s", e)
        return JsonResponse(error_response("Internal Server Error"), status=500)

# Function to update user information
@csrf_exempt
@require_POST
def update_user(request, user_id):
    try:
        if not user_id.isnumeric():
            return JsonResponse(error_response("No such user"), status=404)

        user = get_object_or_404(User, pk=user_id)

        if 'file' in request.FILES:
            avatar_url = upload_image(request.FILES['file'])
            user.avatar = avatar_url

        user.save()

        return JsonResponse(success_response({"message": "User updated successfully"}))
    except Exception as e:
        logger.error("An error occurred during user update: %s", e)
        return JsonResponse(error_response("Internal Server Error"), status=500)

# Helper function for input validation in signup
def validate_signup_request(request):
    try:
        data = json.loads(request.body)
        required_fields = ['userName', 'email', 'password']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"{field} is required")

        # Check for duplicate email
        if CustomUser.objects.filter(email=data['email']).exists():
            raise ValidationError("Email is already in use. Please choose a different email.")

        # Check for duplicate username
        if CustomUser.objects.filter(username=data['userName']).exists():
            raise ValidationError("Username is already in use. Please choose a different username.")

        return data
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON format in request body")




# Helper function for consistent success responses
def success_response(data=None):
    return {"success": True, "data": data}

# Helper function for consistent error responses
def error_response(message, status=400):
    return {"success": False, "error": message}

# Helper function for input validation in sign-in
def validate_sign_in_request(request):
    try:
        data = json.loads(request.body)
        required_fields = ['email', 'password']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"{field} is required")

        return data
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON format in request body")
