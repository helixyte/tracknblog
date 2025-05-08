# blog/views.py (updated)
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from .models import Journey, BlogPost, Comment
from .forms import CommentForm

class JourneyListView(ListView):
    """View for the homepage showing all journeys"""
    model = Journey
    template_name = 'blog/journey_list.html'
    context_object_name = 'journeys'

class JourneyDetailView(ListView):
    """View for a specific journey showing all blog posts for that journey"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'blog_posts'
    
    def get_queryset(self):
        self.journey = get_object_or_404(Journey, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(journey=self.journey)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['journey'] = self.journey
        
        # Get all blog posts with location data for this journey
        posts_with_location = []
        for post in self.get_queryset().filter(latitude__isnull=False, longitude__isnull=False):
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

    def get_object(self):
        self.journey = get_object_or_404(Journey, slug=self.kwargs['journey_slug'])
        return get_object_or_404(BlogPost, pk=self.kwargs['pk'], journey=self.journey)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['journey'] = self.journey
        
        # Add previous and next blog posts for navigation (within the same journey)
        blog_post = self.get_object()
        context['prev_post'] = BlogPost.objects.filter(
            journey=self.journey,
            timestamp__gt=blog_post.timestamp
        ).order_by('timestamp').first()
        context['next_post'] = BlogPost.objects.filter(
            journey=self.journey,
            timestamp__lt=blog_post.timestamp
        ).order_by('-timestamp').first()
        
        # Add comment form and comments to context
        context['comment_form'] = CommentForm()
        # Only get top-level comments (no parent)
        context['comments'] = blog_post.comments.filter(approved=True, parent=None)
        return context

def post_comment(request, journey_slug, pk):
    """Handle comment submission with honeypot and moderation"""
    journey = get_object_or_404(Journey, slug=journey_slug)
    blog_post = get_object_or_404(BlogPost, pk=pk, journey=journey)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # Check honeypot field - if it's filled, it's probably a bot
            if form.cleaned_data.get('website'):
                # Log the bot attempt (optional)
                # Just redirect as if the comment was successful to fool the bot
                return redirect('blog_detail', journey_slug=journey_slug, pk=pk)
            
            # Create comment but don't save to DB yet
            comment = form.save(commit=False)
            comment.blog_post = blog_post
            
            # Store the commenter's IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            comment.ip_address = ip
            
            # Apply moderation if needed
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
            
            return redirect('blog_detail', journey_slug=journey_slug, pk=pk)
    
    # If form is not valid or not POST, return to blog post page
    return redirect('blog_detail', journey_slug=journey_slug, pk=pk)

# API endpoint to get all blog posts with location data as JSON for a specific journey
def blog_locations(request, journey_slug):
    journey = get_object_or_404(Journey, slug=journey_slug)
    posts_with_location = []
    for post in BlogPost.objects.filter(journey=journey, latitude__isnull=False, longitude__isnull=False):
        posts_with_location.append({
            'id': post.id,
            'title': post.title,
            'latitude': post.latitude,
            'longitude': post.longitude
        })
    return JsonResponse(posts_with_location, safe=False)