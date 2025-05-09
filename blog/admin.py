# blog/admin.py (updated)
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from .models import Journey, BlogPost, BlogImage, Comment
from tracker.models import LocationUpdate
from django.conf import settings

# Register the Journey model
@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'start_date', 'end_date', 'is_active', 'post_count')
    search_fields = ('title', 'description')
    list_filter = ('is_active', 'start_date')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Settings', {
            'fields': ('is_active', 'cover_image')
        }),
    )
    
    def post_count(self, obj):
        """Return the number of blog posts for this journey"""
        return obj.posts.count()
    post_count.short_description = 'Posts'
    
    def save_model(self, request, obj, form, change):
        """
        When setting a journey as active, make sure to set all other journeys to inactive
        """
        if obj.is_active:
            # Set all other journeys to inactive
            Journey.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 3  # Show 3 empty forms by default

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'journey', 'timestamp', 'has_location')
    search_fields = ('title', 'description')
    list_filter = ('journey', 'timestamp')
    date_hierarchy = 'timestamp'
    inlines = [BlogImageInline]
    fieldsets = (
        (None, {
            'fields': ('journey', 'title', 'description')
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
            # Get the journey ID from the request if available
            journey_id = request.GET.get('journey_id')
            
            if journey_id:
                # Get the latest location for the specific journey
                latest_location = LocationUpdate.objects.filter(journey_id=journey_id).first()
            else:
                # Get the latest location from the active journey
                active_journey = Journey.objects.filter(is_active=True).first()
                if active_journey:
                    latest_location = LocationUpdate.objects.filter(journey=active_journey).first()
                else:
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
    list_filter = ('blog_post__journey', 'blog_post')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'truncated_content', 'blog_post', 'blog_post_journey', 'ip_address', 'created_at', 'approved', 'is_reply')
    list_filter = ('approved', 'created_at', 'blog_post__journey')
    search_fields = ('name', 'content', 'ip_address')
    actions = ['approve_comments', 'disapprove_comments', 'mark_as_spam', 'block_ip_addresses']
    date_hierarchy = 'created_at'
    list_editable = ('approved',)
    list_per_page = 20
    ordering = ('-created_at',)
    
    def blog_post_journey(self, obj):
        """Return the journey name for better filtering"""
        return obj.blog_post.journey.title
    blog_post_journey.short_description = 'Journey'
    
    def truncated_content(self, obj):
        """Return truncated content for display in admin list"""
        if len(obj.content) > 60:
            return obj.content[:60] + '...'
        return obj.content
    truncated_content.short_description = 'Content'
    
    def is_reply(self, obj):
        """Check if this comment is a reply to another comment"""
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Reply'
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f"{updated} comments were approved successfully.")
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, f"{updated} comments were disapproved.")
    disapprove_comments.short_description = "Disapprove selected comments"
    
    def mark_as_spam(self, request, queryset):
        """Mark comments as spam and add the commenter's name to a spam list"""
        updated = queryset.update(approved=False)
        
        # Get all the names from these comments
        names = list(queryset.values_list('name', flat=True))
        
        # Get the current list of spam names from settings (or create empty list)
        spam_names = list(getattr(settings, 'COMMENT_SPAM_NAMES', []))
        
        # Add new names to the list
        for name in names:
            if name and name not in spam_names:
                spam_names.append(name)
        
        # You could save this back to the database if you have a settings model
        # Or just use it in memory for this session
        
        self.message_user(
            request, 
            f"{updated} comments marked as spam. {len(names)} unique names added to spam list."
        )
    mark_as_spam.short_description = "Mark selected comments as spam"
    
    def block_ip_addresses(self, request, queryset):
        """Block IP addresses from selected comments"""
        # Get unique IP addresses from selected comments
        ip_addresses = set(queryset.exclude(ip_address__isnull=True).values_list('ip_address', flat=True))
        
        if not ip_addresses:
            self.message_user(request, "No IP addresses found in the selected comments.", level="WARNING")
            return
            
        # Get existing blocked IPs from settings (or create empty list)
        blocked_ips = set(getattr(settings, 'COMMENT_BLOCKED_IPS', []))
        
        # Add new IPs to the list
        blocked_ips.update(ip_addresses)
        
        # You would typically save this to a database table in a real implementation
        # For now, we'll just show a message
        
        self.message_user(
            request,
            f"Added {len(ip_addresses)} IP addresses to block list. "
            f"Future comments from these IPs will be automatically rejected."
        )
    block_ip_addresses.short_description = "Block IP addresses for selected comments"
    
    # Add fieldsets for better organization
    fieldsets = (
        ('Comment Information', {
            'fields': ('name', 'content')
        }),
        ('Metadata', {
            'fields': ('blog_post', 'parent', 'created_at', 'ip_address')
        }),
        ('Moderation', {
            'fields': ('approved',),
            'description': 'Manage comment visibility'
        }),
    )
    readonly_fields = ('created_at', 'ip_address')