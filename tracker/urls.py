# tracker/urls.py (updated)
from django.urls import path
from . import views

urlpatterns = [
    # Test endpoint
    path('test/', views.test_endpoint, name='tracker_test'),
    
    # Default routes (use active journey)
    path('update/', views.update_location, name='update_location'),
    path('latest/', views.get_latest_location, name='get_latest_location'),
    path('locations/', views.get_all_locations, name='get_all_locations'),
    
    # Journey-specific routes
    path('journey/<slug:journey_slug>/update/', views.update_location, name='journey_update_location'),
    path('journey/<slug:journey_slug>/latest/', views.get_latest_location, name='journey_get_latest_location'),
    path('journey/<slug:journey_slug>/locations/', views.get_all_locations, name='journey_get_all_locations'),
    
    # Alternative endpoints for different tracking apps
    path('owntracks/', views.update_location, name='owntracks_update'),
    path('traccar/', views.update_location, name='traccar_update'),
    path('overland/', views.update_location, name='overland_update'),
]