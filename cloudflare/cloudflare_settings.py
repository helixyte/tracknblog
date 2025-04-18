# cloudflare_settings.py
# Import base settings
from .settings import *

# Domain configuration
ALLOWED_HOSTS = ['vista-grande.net', 'www.vista-grande.net']

# Configure for running in a subdirectory
FORCE_SCRIPT_NAME = '/blog'
STATIC_URL = '/blog/static/'
MEDIA_URL = '/blog/media/'

# Base URL for templates and JavaScript
BASE_URL = 'https://vista-grande.net/blog'

# Static and media files for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Cloudflare settings
# Trusting Cloudflare's proxy
CLOUDFLARE_IPS = [
    # IPv4 ranges
    '173.245.48.0/20',
    '103.21.244.0/22',
    '103.22.200.0/22',
    '103.31.4.0/22',
    '141.101.64.0/18',
    '108.162.192.0/18',
    '190.93.240.0/20',
    '188.114.96.0/20',
    '197.234.240.0/22',
    '198.41.128.0/17',
    '162.158.0.0/15',
    '104.16.0.0/13',
    '104.24.0.0/14',
    '172.64.0.0/13',
    '131.0.72.0/22',
    # IPv6 ranges
    '2400:cb00::/32',
    '2606:4700::/32',
    '2803:f800::/32',
    '2405:b500::/32',
    '2405:8100::/32',
    '2a06:98c0::/29',
    '2c0f:f248::/32',
]

# Update the MIDDLEWARE to include Cloudflare middleware
MIDDLEWARE = [
    # Add any Cloudflare middleware if needed
] + MIDDLEWARE

# Example cloudflare middleware to get real IP
class CloudflareMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the real IP from Cloudflare
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            request.META['REMOTE_ADDR'] = cf_connecting_ip
        
        response = self.get_response(request)
        return response

# Add the middleware to the list
MIDDLEWARE.insert(0, 'path.to.CloudflareMiddleware')
