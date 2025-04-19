# blog/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import BlogPost

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'blog_posts'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all blog posts with location data
        posts_with_location = []
        for post in BlogPost.objects.filter(latitude__isnull=False, longitude__isnull=False):
            posts_with_location.append({
                'id': post.id,
                'title': post.title,
                'latitude': post.latitude,
                'longitude': post.longitude
            })
        context['blog_posts_with_location'] = posts_with_location
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'blog_post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add previous and next blog posts for navigation
        blog_post = self.get_object()
        context['prev_post'] = BlogPost.objects.filter(
            timestamp__gt=blog_post.timestamp
        ).order_by('timestamp').first()
        context['next_post'] = BlogPost.objects.filter(
            timestamp__lt=blog_post.timestamp
        ).order_by('-timestamp').first()
        return context

# API endpoint to get all blog posts with location data as JSON
def blog_locations(request):
    posts_with_location = []
    for post in BlogPost.objects.filter(latitude__isnull=False, longitude__isnull=False):
        posts_with_location.append({
            'id': post.id,
            'title': post.title,
            'latitude': post.latitude,
            'longitude': post.longitude
        })
    return JsonResponse(posts_with_location, safe=False)