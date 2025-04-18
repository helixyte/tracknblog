# bicycle_blog/context_processors.py
from django.conf import settings

def base_url_processor(request):
    """Add BASE_URL to the template context"""
    return {} # 'BASE_URL': settings.BASE_URL}
