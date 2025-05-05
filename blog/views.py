# blog/views.py
# blog/views.py (updated imports)
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
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
        # Only get top-level comments (no parent)
        context['comments'] = blog_post.comments.filter(approved=True, parent=None)
        return context

# blog/views.py (updated post_comment function)

def post_comment(request, pk):
    """Handle comment submission with honeypot and moderation"""
    blog_post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # Check honeypot field - if it's filled, it's probably a bot
            if form.cleaned_data.get('website'):
                # Log the bot attempt (optional)
                # Just redirect as if the comment was successful to fool the bot
                return redirect('blog_detail', pk=blog_post.pk)
            
            # Create comment but don't save to DB yet
            comment = form.save(commit=False)
            comment.blog_post = blog_post
            
            # Apply moderation if needed
            # Set approved to False if automatic moderation is enabled
            # or if specific keywords are present
            auto_moderate = getattr(settings, 'AUTO_MODERATE_COMMENTS', False)
            moderation_keywords = getattr(settings, 'COMMENT_MODERATION_KEYWORDS', 
                                         ['viagra', 'cialis', 'casino', 'pharmacy'])
            
            content_lower = comment.content.lower()
            if auto_moderate or any(keyword in content_lower for keyword in moderation_keywords):
                comment.approved = False
            
            # Save the comment
            comment.save()
            
            # Show a success message to the user
            messages.success(request, 
                            'Your comment has been submitted and is awaiting moderation.' 
                            if not comment.approved else 
                            'Your comment has been posted successfully.')
            
            return redirect('blog_detail', pk=blog_post.pk)
    
    # If form is not valid or not POST, return to blog post page
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