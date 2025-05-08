# tracnblog/context_processors.py
from django.conf import settings
from blog.models import Journey

def base_url_processor(request):
    """Add BASE_URL to the template context"""
    return {'BASE_URL': getattr(settings, 'BASE_URL', '')}

def active_journey_processor(request):
    """Add the active journey to the template context"""
    active_journey = Journey.objects.filter(is_active=True).first()
    return {'active_journey': active_journey}