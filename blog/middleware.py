# blog/middleware.py
from django.core.cache import cache
from django.http import HttpResponseForbidden
import time
from django.conf import settings
from django.contrib import messages

class CommentRateLimitMiddleware:
    """
    Middleware to rate limit comment submissions based on IP address.
    
    This prevents spam and abuse by limiting how frequently users can post comments.
    Also blocks comments from known spammer IP addresses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only apply rate limiting to the comment view
        if view_func.__name__ == 'post_comment' and request.method == 'POST':
            # Get client IP address
            ip_address = self._get_client_ip(request)
            
            # Check if this IP is blocked
            blocked_ips = getattr(settings, 'COMMENT_BLOCKED_IPS', [])
            if ip_address in blocked_ips:
                messages.error(request, "Comments from your IP address are not permitted.")
                return HttpResponseForbidden("Your IP address has been blocked from commenting.")
            
            # Set rate limiting parameters from settings
            rate_limit_time = getattr(settings, 'COMMENT_RATE_LIMIT_TIME', 60)  # seconds
            max_comments = getattr(settings, 'COMMENT_RATE_LIMIT_COUNT', 3)     # max comments per time period
            
            # Get cache key for this IP
            cache_key = f'comment_rate_limit_{ip_address}'
            
            # Get current rate limit data from cache
            rate_data = cache.get(cache_key, {'count': 0, 'first_attempt': time.time()})
            
            # If the time window has expired, reset the counter
            current_time = time.time()
            if current_time - rate_data['first_attempt'] > rate_limit_time:
                rate_data = {'count': 0, 'first_attempt': current_time}
            
            # Check if the user has exceeded the limit
            if rate_data['count'] >= max_comments:
                messages.error(
                    request,
                    f"You've submitted too many comments. Please wait {int(rate_limit_time/60)} minutes before trying again."
                )
                
                return HttpResponseForbidden(
                    "Comment rate limit exceeded. Please wait before posting again."
                )
            
            # Increment the counter and update the cache
            rate_data['count'] += 1
            cache.set(cache_key, rate_data, rate_limit_time * 2)  # Keep in cache twice as long as the window
        
        # Allow the request to proceed
        return None
    
    def _get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip