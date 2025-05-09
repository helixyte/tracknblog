# tracker/views.py (updated)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json
from .models import LocationUpdate
from blog.models import Journey

@csrf_exempt
@require_POST
def update_location(request, journey_slug=None):
    """API endpoint to receive location updates from iPhone using Overland"""
    try:
        # Get the journey, default to the active one if not specified
        if journey_slug:
            journey = get_object_or_404(Journey, slug=journey_slug)
        else:
            journey = Journey.objects.filter(is_active=True).first()
            
        if not journey:
            return JsonResponse({'status': 'error', 'message': 'No active journey found'}, status=404)
        
        data = json.loads(request.body)
        
        # Check if this is Overland format
        if 'locations' in data and isinstance(data['locations'], list):
            # Process each location in the batch
            for location in data['locations']:
                if 'geometry' in location and 'coordinates' in location['geometry']:
                    # Extract coordinates (Overland uses [longitude, latitude] order)
                    coords = location['geometry']['coordinates']
                    lng = coords[0]
                    lat = coords[1]
                    
                    # Save to database with journey
                    if lat and lng:
                        location_obj = LocationUpdate(latitude=lat, longitude=lng, journey=journey)
                        location_obj.save()
            
            return JsonResponse({'status': 'success'})
        else:
            # Handle original format
            lat = data.get('latitude')
            lng = data.get('longitude')
            
            if lat and lng:
                location = LocationUpdate(latitude=lat, longitude=lng, journey=journey)
                location.save()
                return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'error', 'message': 'Missing coordinates'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_latest_location(request, journey_slug=None):
    """API endpoint to retrieve the latest location for the map"""
    try:
        # Get the journey, default to the active one if not specified
        if journey_slug:
            journey = get_object_or_404(Journey, slug=journey_slug)
        else:
            journey = Journey.objects.filter(is_active=True).first()
            
        if not journey:
            return JsonResponse({'status': 'error', 'message': 'No active journey found'}, status=404)
        
        latest = LocationUpdate.objects.filter(journey=journey).first()  # Using the Meta ordering
        if latest:
            return JsonResponse({
                'latitude': latest.latitude,
                'longitude': latest.longitude,
                'timestamp': latest.timestamp.isoformat()
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'No location data available'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)