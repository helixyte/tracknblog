# blog/urls.py (updated)
from django.urls import path
from . import views

urlpatterns = [
    # Journey URLs
    path('', views.JourneyListView.as_view(), name='journey_list'),  # Homepage - list of all journeys
    path('journey/<slug:slug>/', views.JourneyDetailView.as_view(), name='journey_detail'),  # List of posts for a journey
    
    # Blog post URLs
    path('journey/<slug:journey_slug>/post/<int:pk>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('journey/<slug:journey_slug>/post/<int:pk>/comment/', views.post_comment, name='post_comment'),
    
    # API URLs
    path('api/journey/<slug:journey_slug>/locations/', views.blog_locations, name='blog_locations')
]