# tracker/models.py (updated)
from django.db import models

class LocationUpdate(models.Model):
    journey = models.ForeignKey('blog.Journey', related_name='locations', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Location for {self.journey.title} at {self.timestamp}"