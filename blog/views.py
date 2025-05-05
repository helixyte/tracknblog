# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.http import JsonResponse
from .models import BlogPost, Comment
from .forms import CommentForm

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
        
        # Add comment form and comments to context
        context['comment_form'] = CommentForm()
        context['comments'] = blog_post.comments.filter(approved=True)
        return context

def post_comment(request, pk):
    """Handle comment submission"""
    blog_post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog_post = blog_post
            comment.save()
            return redirect('blog_detail', pk=blog_post.pk)
    
    # If form is not valid, return to blog post page with form errors
    return redirect('blog_detail', pk=blog_post.pk)

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