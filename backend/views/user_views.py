import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
import json
import bcrypt
import jwt
import logging
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.core.validators import validate_email
from django.core.serializers import serialize
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.password_validation import validate_password
from backend.models import CustomUser
from django.contrib.auth import authenticate, login
import traceback
from django.http import HttpResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        access_token = response.data["access"]
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            domain=settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
        return response





@csrf_exempt
@require_POST
def signup(request):
    try:
        # print("Request Data:", request.body)
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
        hashed_pass_bytes = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt(12))
        hashed_pass_str = hashed_pass_bytes.decode('utf-8') 
        # print("hashed_pass",hashed_pass)
        # Create a new user object with hashed password
        new_user = CustomUser(
            username=data['userName'],
            email=data['email'],
            password=hashed_pass_str  
        )
        print("new_user",new_user.password)
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


# ...

# ... (existing code)

@csrf_exempt
@require_POST
def sign_in(request):
    try:
        data = validate_sign_in_request(request)
        print("Validated Data:", data)

        email = data.get('email')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return JsonResponse(error_response("User not found"), status=404)

        hashed_password_bytes = user.password.encode('utf-8')
        print("Hashed Password in Database:", hashed_password_bytes)

        password_matches = bcrypt.checkpw(password.encode('utf-8'), hashed_password_bytes)
        print("Password Matches:", password_matches)

        if password_matches:
            # Generate a JWT token
            jwt_token = generate_jwt_token(user)

            # Set cookies and return success response
            response = JsonResponse(success_response({"message": "Login successful"}))
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=jwt_token,
                domain=settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
                path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
                expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )
            return response

        # Handle unsuccessful authentication
        print("Authentication failed.")
        return JsonResponse(error_response("Invalid credentials"), status=401)

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format in the request body"}, status=400)
    except Exception as e:
        print("Error during sign-in:", e)
        traceback.print_exc()
        return JsonResponse({"error": "An unexpected error occurred during sign-in"}, status=500)



# Add a function to generate JWT token
def generate_jwt_token(user):
    # Replace 'your_secret_key' with your actual secret key
    SECRET_KEY = os.getenv('SECRET_KEY')
    payload = {
        'id': user.id,
        'userName': user.username,
        # 'avatar': user.avatar,  # Add the necessary user attributes
    }

    # Use a library or method to generate a JWT token
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return jwt_token

# Define validate_sign_in_request, success_response, and error_response functions here
# ...

# Function to verify user token
def verify_user(request):
    try:
        token = request.headers.get('Authorization', '').replace("Bearer ", "")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        return JsonResponse(success_response({
            "userId": decoded['id'],
            "username": decoded['userName'],
            "avatar": decoded['avatar'],
        }))
    except jwt.ExpiredSignatureError:
        return JsonResponse(error_response("Token has expired"), status=401)
    except jwt.InvalidTokenError:
        return JsonResponse(error_response("Invalid token"), status=401)

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
