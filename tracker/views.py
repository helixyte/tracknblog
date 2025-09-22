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
from .coordinates import parse_coordinate_pair

logger = logging.getLogger(__name__)

def _to_float_or_none(value):
    """Convert a value to float when possible, otherwise return None."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    return None


def _extract_coordinates(lat, lng, possible_sources=None):
    """Ensure latitude/longitude are floats, checking alternate sources if needed."""
    lat_value = _to_float_or_none(lat)
    lng_value = _to_float_or_none(lng)

    if lat_value is not None and lng_value is not None:
        return lat_value, lng_value

    combined_candidates = []

    if isinstance(lat, str):
        combined_candidates.append(lat)
    if isinstance(lng, str):
        combined_candidates.append(lng)

    if possible_sources:
        for key in ("location", "coordinates", "coord", "point"):
            if key in possible_sources:
                combined_value = possible_sources.get(key)
                if not combined_value:
                    continue
                if isinstance(combined_value, (list, tuple)) and len(combined_value) == 2:
                    try:
                        return float(combined_value[0]), float(combined_value[1])
                    except (TypeError, ValueError):
                        continue
                if isinstance(combined_value, str):
                    combined_candidates.append(combined_value)

    for candidate in combined_candidates:
        parsed = parse_coordinate_pair(candidate)
        if parsed:
            return parsed

    return lat_value, lng_value


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
        
        request_payload = None

        if request.method == 'POST':
            # Handle POST requests (OwnTracks, Overland, custom)
            try:
                request_payload = json.loads(request.body)
                data = request_payload
                logger.info(f"Received POST data: {data}")
                
                # OwnTracks format - handle different message types
                if '_type' in data:
                    msg_type = data.get('_type')
                    logger.info(f"OwnTracks message type: {msg_type}")
                    
                    if msg_type == 'location':
                        # Location update - this is what we want
                        lat = data.get('lat')
                        lng = data.get('lon')
                        timestamp = data.get('tst')  # Unix timestamp
                        accuracy = data.get('acc')
                        battery = data.get('batt')
                        logger.info("Processing OwnTracks location update")
                    
                    elif msg_type == 'waypoints':
                        # Waypoints message - acknowledge but don't process
                        logger.info("Received OwnTracks waypoints message - acknowledging")
                        return JsonResponse({'status': 'success', 'message': 'Waypoints acknowledged'})
                    
                    elif msg_type == 'transition':
                        # Geofence transition - acknowledge but don't process
                        logger.info("Received OwnTracks transition message - acknowledging")
                        return JsonResponse({'status': 'success', 'message': 'Transition acknowledged'})
                    
                    elif msg_type == 'lwt':
                        # Last Will and Testament message - acknowledge
                        logger.info("Received OwnTracks LWT message - acknowledging")
                        return JsonResponse({'status': 'success', 'message': 'LWT acknowledged'})
                    
                    elif msg_type == 'card':
                        # Contact card - acknowledge
                        logger.info("Received OwnTracks card message - acknowledging")
                        return JsonResponse({'status': 'success', 'message': 'Card acknowledged'})
                    
                    elif msg_type == 'status':
                        # Device status message - acknowledge and log useful info
                        logger.info("Received OwnTracks status message - acknowledging")
                        ios_info = data.get('iOS', {})
                        auth_status = ios_info.get('locationManagerAuthorizationStatus', 'unknown')
                        background_status = ios_info.get('backgroundRefreshStatus', 'unknown')
                        logger.info(f"Location auth: {auth_status}, Background refresh: {background_status}")
                        return JsonResponse({'status': 'success', 'message': 'Status acknowledged'})
                    
                    else:
                        # Unknown OwnTracks message type - acknowledge anyway
                        logger.info(f"Received unknown OwnTracks message type: {msg_type} - acknowledging")
                        return JsonResponse({'status': 'success', 'message': f'Message type {msg_type} acknowledged'})
                
                # Check if this is still OwnTracks format but with 'lat'/'lon' keys
                elif 'lat' in data and 'lon' in data:
                    lat = data.get('lat')
                    lng = data.get('lon')
                    timestamp = data.get('tst')
                    accuracy = data.get('acc')
                    battery = data.get('batt')
                    logger.info("Detected OwnTracks location format (without _type)")
                
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
            
            logger.info("Detected Traccar Client format")

        # Normalize coordinates (support combined latitude/longitude strings)
        sources = request_payload if isinstance(request_payload, dict) else request.GET
        lat, lng = _extract_coordinates(lat, lng, possible_sources=sources)

        # Save the location if we have valid coordinates
        if lat is not None and lng is not None:
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

@csrf_exempt
def get_all_locations(request, journey_slug=None):
    """API endpoint to retrieve all location updates for the journey map"""
    try:
        # Get the journey, default to the active one if not specified
        if journey_slug:
            journey = get_object_or_404(Journey, slug=journey_slug)
        else:
            journey = Journey.objects.filter(is_active=True).first()
            
        if not journey:
            return JsonResponse({'status': 'error', 'message': 'No active journey found'}, status=404)
        
        locations = LocationUpdate.objects.filter(journey=journey).order_by('timestamp')
        location_data = []
        
        for location in locations:
            location_data.append({
                'latitude': location.latitude,
                'longitude': location.longitude,
                'timestamp': location.timestamp.isoformat(),
            })
        
        return JsonResponse({
            'status': 'success',
            'locations': location_data,
            'journey': journey.title,
            'total_count': len(location_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting all locations: {e}")
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