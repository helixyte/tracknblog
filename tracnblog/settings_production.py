from .settings import *  # Import base settings

# Base URL for templates and JavaScript
BASE_URL = 'https://goeast.vista-grande.net'


# Set production settings
DEBUG = False
ALLOWED_HOSTS = ['goeast.vista-grande.net']

# Security settings for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True