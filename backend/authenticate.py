# backend/authenticate.py

from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    # Your custom authentication logic here
    pass  # Add this pass statement if you don't have any logic yet
