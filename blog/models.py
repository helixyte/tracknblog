# blog/models.py (updated with Journey model)
import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from PIL import Image

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
    HEIF_SUPPORTED = True
except ImportError:  # pragma: no cover - pillow-heif should be installed via requirements
    HEIF_SUPPORTED = False


def _convert_heif_image(field_file):
    """Convert HEIF/HEIC images to JPEG so Pillow can process them reliably."""

    if not field_file or not getattr(field_file, "name", None):
        return

    ext = os.path.splitext(field_file.name)[1].lower()
    if ext not in {".heic", ".heif"}:
        return

    if not HEIF_SUPPORTED:
        return

    file_obj = getattr(field_file, "file", None)
    if file_obj is None:
        return

    file_obj.seek(0)
    image = Image.open(file_obj)
    converted = image.convert("RGB")

    buffer = BytesIO()
    converted.save(buffer, format="JPEG")
    image.close()
    converted.close()

    buffer.seek(0)
    new_name = os.path.splitext(field_file.name)[0] + ".jpg"
    field_file.save(new_name, ContentFile(buffer.getvalue()), save=False)

class Journey(models.Model):
    """
    Represents a complete bicycle journey/trip.
    Each journey can have multiple blog posts and location updates.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='journey_covers/', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Journeys"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('journey_detail', args=[str(self.slug)])
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.title)
        if self.cover_image:
            _convert_heif_image(self.cover_image)
        super().save(*args, **kwargs)
    
    @property
    def latest_post(self):
        """Return the latest blog post for this journey"""
        return self.posts.first()
    
    @property
    def latest_location(self):
        """Return the latest location update for this journey"""
        return self.locations.first()

class BlogPost(models.Model):
    journey = models.ForeignKey(Journey, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'journey_slug': self.journey.slug, 'pk': self.pk})
    
    @property
    def first_image(self):
        """Return the first image for this blog post"""
        image = self.images.first()
        return image if image else None

    @property
    def has_location(self):
        """Check if this blog post has location data"""
        return self.latitude is not None and self.longitude is not None

class BlogImage(models.Model):
    blog_post = models.ForeignKey(BlogPost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_images/')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.blog_post.title}"

    def save(self, *args, **kwargs):
        if self.image:
            _convert_heif_image(self.image)
        super().save(*args, **kwargs)

class Comment(models.Model):
    blog_post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.name} on {self.blog_post.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None