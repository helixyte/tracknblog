# tracker/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import LocationUpdate

@csrf_exempt
@require_POST
def update_location(request):
    """API endpoint to receive location updates from iPhone"""
    try:
        data = json.loads(request.body)
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat and lng:
            location = LocationUpdate(latitude=lat, longitude=lng)
            location.save()
            return JsonResponse({'status': 'success'})
        else:
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
