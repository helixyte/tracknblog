# blog/models.py (updated with Journey model)
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

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