# tracker/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import LocationUpdate

@csrf_exempt
@require_POST
def update_location(request):
    """API endpoint to receive location updates from iPhone using Overland"""
    try:
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
                    
                    # Save to database
                    if lat and lng:
                        location_obj = LocationUpdate(latitude=lat, longitude=lng)
                        location_obj.save()
            
            return JsonResponse({'status': 'success'})
        else:
            # Handle original format
            lat = data.get('latitude')
            lng = data.get('longitude')
            
            if lat and lng:
                location = LocationUpdate(latitude=lat, longitude=lng)
                location.save()
                return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'error', 'message': 'Missing coordinates'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_latest_location(request):
    """API endpoint to retrieve the latest location for the map"""
    try:
        latest = LocationUpdate.objects.first()  # Using the Meta ordering
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
