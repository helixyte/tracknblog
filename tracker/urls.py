# tracker/urls.py (updated)
from django.urls import path
from . import views

urlpatterns = [
    # Default routes (use active journey)
    path('update/', views.update_location, name='update_location'),
    path('latest/', views.get_latest_location, name='get_latest_location'),
    
    # Journey-specific routes
    path('journey/<slug:journey_slug>/update/', views.update_location, name='journey_update_location'),
    path('journey/<slug:journey_slug>/latest/', views.get_latest_location, name='journey_get_latest_location'),
]