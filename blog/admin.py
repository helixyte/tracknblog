# blog/admin.py
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from .models import BlogPost, BlogImage, Comment
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
            'description': 'Click "Get Current Location" button to auto-fill with your latest location data.'
        })
    )
    
    class Media:
        js = ('blog/admin/js/admin_geolocation.js',)
    
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

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'blog_post', 'created_at', 'approved')
    list_filter = ('approved', 'created_at', 'blog_post')
    search_fields = ('name', 'email', 'content')
    actions = ['approve_comments', 'disapprove_comments']
    date_hierarchy = 'created_at'
    
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, f"{queryset.count()} comments approved.")
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, f"{queryset.count()} comments disapproved.")
    disapprove_comments.short_description = "Disapprove selected comments"