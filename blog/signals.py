# blog/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import BlogPost
from tracker.models import LocationUpdate

@receiver(pre_save, sender=BlogPost)
def populate_blog_location(sender, instance, **kwargs):
    """
    Auto-populate blog post location with the latest location data
    when a new blog post is created and has no location data.
    """
    # Only populate if the blog post doesn't already have location data
    if not instance.has_location:
        # Try to get the latest location update
        try:
            latest_location = LocationUpdate.objects.first()  # First due to ordering in Meta
            if latest_location:
                instance.latitude = latest_location.latitude
                instance.longitude = latest_location.longitude
        except LocationUpdate.DoesNotExist:
            # No location data available, leave it blank
            pass