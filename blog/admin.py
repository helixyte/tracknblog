# blog/admin.py
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils.html import format_html
from .models import BlogPost, BlogImage
from tracker.models import LocationUpdate

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 3  # Show 3 empty forms by default

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'timestamp', 'has_location')
    search_fields = ('title', 'description')
    date_hierarchy = 'timestamp'
    inlines = [BlogImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'description': format_html('''
                Click the button below to auto-fill with your latest location data.<br><br>
                <button type="button" onclick="getLatestLocation()" 
                        style="margin: 10px 0; padding: 8px 15px; font-size: 14px; 
                               background-color: #0078d7; color: white; border: none; 
                               border-radius: 4px; cursor: pointer;">
                    Get Current Location
                </button>
            ''')
        })
    )
    
    class Media:
        js = ('blog/admin/location_button.js',)
    
    def has_location(self, obj):
        return obj.latitude is not None and obj.longitude is not None
    has_location.boolean = True
    has_location.short_description = 'Has Location'
    
    def get_urls(self):
        """Add custom URL for getting the latest location"""
        urls = super().get_urls()
        custom_urls = [
            path('get-latest-location/', self.admin_site.admin_view(self.get_latest_location), name='blog_blogpost_get_latest_location'),
        ]
        return custom_urls + urls
    
    def get_latest_location(self, request):
        """
        Custom admin view to return the latest location from the tracker
        """
        try:
            latest_location = LocationUpdate.objects.first()  # Gets the latest due to model ordering
            if latest_location:
                return JsonResponse({
                    'success': True,
                    'latitude': latest_location.latitude,
                    'longitude': latest_location.longitude,
                    'timestamp': latest_location.timestamp.isoformat()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No location data available'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'order')
    list_filter = ('blog_post',)
