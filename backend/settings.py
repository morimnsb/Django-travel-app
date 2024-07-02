import os
from decouple import config
from dotenv import load_dotenv
from datetime import timedelta
# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config('SECRET')

DEBUG = True

SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SAMESITE = None



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'backend.CustomUser'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend',
    'corsheaders',  # Make sure 'corsheaders' appears only once
    'rest_framework',
    "rest_framework_simplejwt.token_blacklist",
]



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'backend.authenticate.CustomJWTAuthentication',  # our custom JWT authentication class - it is created below
    )
}

if DEBUG:
    INSTALLED_APPS += ['webpack_loader']

    WEBPACK_LOADER = {
        'DEFAULT': {
            'BUNDLE_DIR_NAME': 'bundles/',
            'STATS_FILE': os.path.join(BASE_DIR, 'backend', 'my-react-app', 'src', 'webpack-stats.json'),
        }
    }

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]
PASSWORD_HASHERS = [
    # ...
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    # ...
]

# Templates
TEMPLATES = [
    {
        'APP_DIRS': True,
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'travelapp/templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'backend', 'build', 'static'),
    # other directories...
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOW_CREDENTIALS = True
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    'BLACKLIST_AFTER_ROTATION': True,

    # custom
    "AUTH_COOKIE": "access_token",  # cookie name
    "AUTH_COOKIE_DOMAIN": None,  # specifies domain for which the cookie will be sent
    "AUTH_COOKIE_SECURE": False,  # restricts the transmission of the cookie to only occur over secure (HTTPS) connections. 
    "AUTH_COOKIE_HTTP_ONLY": True,  # prevents client-side js from accessing the cookie
    "AUTH_COOKIE_PATH": "/",  # URL path where cookie will be sent
    "AUTH_COOKIE_SAMESITE": "Lax",  # specifies whether the cookie should be sent in cross site requests
}
# Database settings
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': config('DB_NAME', default='your_database_name'),
        'USER': config('DB_USER', default='your_database_user'),
        'PASSWORD': config('DB_PASSWORD', default='your_database_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306', cast=int),
    }
}

CORS_ALLOW_ALL_ORIGINS = True
ROOT_URLCONF = 'backend.urls'
