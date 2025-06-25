# tracker/views.py (updated for OwnTracks and Traccar Client)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
import logging
from .models import LocationUpdate
from blog.models import Journey

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def update_location(request, journey_slug=None):
    """
    API endpoint to receive location updates from various tracking apps:
    - OwnTracks (POST with JSON)
    - Traccar Client (GET with query parameters)
    - Overland (POST with JSON)
    - Custom format (POST with JSON)
    """
    try:
        # Get the journey, default to the active one if not specified
        if journey_slug:
            journey = get_object_or_404(Journey, slug=journey_slug)
        else:
            journey = Journey.objects.filter(is_active=True).first()
            
        if not journey:
            logger.error("No active journey found")
            return JsonResponse({'status': 'error', 'message': 'No active journey found'}, status=404)
        
        lat = None
        lng = None
        timestamp = None
        accuracy = None
        battery = None
        
        if request.method == 'POST':
            # Handle POST requests (OwnTracks, Overland, custom)
            try:
                data = json.loads(request.body)
                logger.info(f"Received POST data: {data}")
                
                # OwnTracks format
                if data.get('_type') == 'location':
                    lat = data.get('lat')
                    lng = data.get('lon')
                    timestamp = data.get('tst')  # Unix timestamp
                    accuracy = data.get('acc')
                    battery = data.get('batt')
                    logger.info("Detected OwnTracks format")
                
                # Overland format (array of locations)
                elif 'locations' in data and isinstance(data['locations'], list):
                    logger.info("Detected Overland format")
                    # Process each location in the batch
                    locations_saved = 0
                    for location in data['locations']:
                        if 'geometry' in location and 'coordinates' in location['geometry']:
                            # Extract coordinates (Overland uses [longitude, latitude] order)
                            coords = location['geometry']['coordinates']
                            loc_lng = coords[0]
                            loc_lat = coords[1]
                            
                            # Get timestamp if available
                            loc_timestamp = location.get('properties', {}).get('timestamp')
                            
                            if loc_lat and loc_lng:
                                location_obj = LocationUpdate(
                                    latitude=loc_lat, 
                                    longitude=loc_lng, 
                                    journey=journey
                                )
                                location_obj.save()
                                locations_saved += 1
                    
                    return JsonResponse({
                        'status': 'success', 
                        'message': f'Saved {locations_saved} locations'
                    })
                
                # Custom format (original)
                else:
                    lat = data.get('latitude')
                    lng = data.get('longitude')
                    logger.info("Detected custom format")
                    
            except json.JSONDecodeError:
                logger.error("Invalid JSON in POST request")
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        
        elif request.method == 'GET':
            # Handle GET requests (Traccar Client)
            logger.info(f"Received GET parameters: {dict(request.GET)}")
            
            # Traccar Client format
            lat = request.GET.get('lat')
            lng = request.GET.get('lon')
            if not lat:
                lat = request.GET.get('latitude')
            if not lng:
                lng = request.GET.get('longitude')
            
            # Additional Traccar parameters
            timestamp = request.GET.get('timestamp')
            accuracy = request.GET.get('accuracy')
            battery = request.GET.get('batt')
            
            # Convert string coordinates to float
            if lat:
                lat = float(lat)
            if lng:
                lng = float(lng)
                
            logger.info("Detected Traccar Client format")
        
        # Save the location if we have valid coordinates
        if lat and lng:
            try:
                location = LocationUpdate(
                    latitude=lat, 
                    longitude=lng, 
                    journey=journey
                )
                
                # Set custom timestamp if provided
                if timestamp:
                    try:
                        # Handle Unix timestamp
                        if isinstance(timestamp, (int, float)) or (isinstance(timestamp, str) and timestamp.isdigit()):
                            from datetime import datetime
                            location.timestamp = datetime.fromtimestamp(float(timestamp), tz=timezone.get_current_timezone())
                        # Handle ISO timestamp
                        elif isinstance(timestamp, str):
                            from django.utils.dateparse import parse_datetime
                            parsed_time = parse_datetime(timestamp)
                            if parsed_time:
                                location.timestamp = parsed_time
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Could not parse timestamp {timestamp}: {e}")
                
                location.save()
                logger.info(f"Saved location: {lat}, {lng} for journey {journey.title}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Location updated successfully',
                    'latitude': lat,
                    'longitude': lng,
                    'journey': journey.title
                })
                
            except Exception as e:
                logger.error(f"Error saving location: {e}")
                return JsonResponse({'status': 'error', 'message': 'Database error'}, status=500)
        
        logger.warning("No valid coordinates received")
        return JsonResponse({'status': 'error', 'message': 'Missing or invalid coordinates'}, status=400)
        
    except Exception as e:
        logger.error(f"Unexpected error in update_location: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
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
                'status': 'success',
                'latitude': latest.latitude,
                'longitude': latest.longitude,
                'timestamp': latest.timestamp.isoformat(),
                'journey': journey.title
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'No location data available'}, status=404)
    except Exception as e:
        logger.error(f"Error getting latest location: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# Test endpoint to verify the API is working
@csrf_exempt
def test_endpoint(request):
    """Test endpoint to verify API connectivity"""
    return JsonResponse({
        'status': 'success',
        'message': 'Tracker API is working',
        'timestamp': timezone.now().isoformat(),
        'method': request.method,
        'active_journey': Journey.objects.filter(is_active=True).first().title if Journey.objects.filter(is_active=True).exists() else None
    })