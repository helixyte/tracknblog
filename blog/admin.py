# blog/admin.py
from django.contrib import admin
from .models import BlogPost, BlogImage

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 3  # Show 3 empty forms by default

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'timestamp')
    search_fields = ('title', 'description')
    date_hierarchy = 'timestamp'
    inlines = [BlogImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'description': 'Coordinates for this blog post'
        })
        )

    def has_location(self, obj):
        return obj.latitude is not None and obj.longitude is not None
    has_location.boolean = True
    has_location.short_description = 'Has Location'

@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'order')
    list_filter = ('blog_post',)
