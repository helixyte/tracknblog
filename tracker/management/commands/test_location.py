# tracker/management/commands/test_location.py
from django.core.management.base import BaseCommand, CommandError
from blog.models import Journey
from tracker.models import LocationUpdate
import requests
import json

class Command(BaseCommand):
    help = 'Test location tracking endpoints with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='http://localhost:8000/tracker/update/',
            help='Base URL for the tracker API (default: http://localhost:8000/tracker/update/)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['owntracks', 'traccar', 'custom'],
            default='custom',
            help='Format to test (default: custom)'
        )
        parser.add_argument(
            '--journey',
            type=str,
            help='Journey slug to use for testing'
        )

    def handle(self, *args, **options):
        base_url = options['url']
        format_type = options['format']
        journey_slug = options['journey']
        
        # Test coordinates (somewhere in Europe for a bike trip)
        test_lat = 52.5200  # Berlin latitude
        test_lng = 13.4050  # Berlin longitude
        
        # Get journey info
        if journey_slug:
            try:
                journey = Journey.objects.get(slug=journey_slug)
                self.stdout.write(f"Testing with journey: {journey.title}")
                url = base_url.replace('/update/', f'/journey/{journey_slug}/update/')
            except Journey.DoesNotExist:
                raise CommandError(f'Journey "{journey_slug}" does not exist')
        else:
            journey = Journey.objects.filter(is_active=True).first()
            if journey:
                self.stdout.write(f"Testing with active journey: {journey.title}")
            else:
                self.stdout.write("No active journey found - will create a location anyway")
            url = base_url
        
        self.stdout.write(f"Testing URL: {url}")
        self.stdout.write(f"Format: {format_type}")
        
        # Test different formats
        if format_type == 'owntracks':
            self.test_owntracks_format(url, test_lat, test_lng)
        elif format_type == 'traccar':
            self.test_traccar_format(url, test_lat, test_lng)
        else:
            self.test_custom_format(url, test_lat, test_lng)
        
        # Show the latest location from database
        self.show_latest_location(journey)

    def test_owntracks_format(self, url, lat, lng):
        """Test OwnTracks JSON format"""
        self.stdout.write("\n--- Testing OwnTracks format ---")
        
        payload = {
            "_type": "location",
            "lat": lat,
            "lon": lng,
            "tst": 1640995200,  # Unix timestamp
            "acc": 10,          # Accuracy in meters
            "batt": 95,         # Battery percentage
            "tid": "TB"         # Tracker ID (Test Bike)
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            self.stdout.write(f"Status Code: {response.status_code}")
            self.stdout.write(f"Response: {response.text}")
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✅ OwnTracks format test PASSED"))
            else:
                self.stdout.write(self.style.ERROR("❌ OwnTracks format test FAILED"))
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection error: {e}"))

    def test_traccar_format(self, url, lat, lng):
        """Test Traccar GET format"""
        self.stdout.write("\n--- Testing Traccar format ---")
        
        params = {
            'id': 'test-bike-001',
            'timestamp': 1640995200,
            'lat': lat,
            'lon': lng,
            'speed': 0,
            'bearing': 180,
            'altitude': 100,
            'accuracy': 10,
            'batt': 95
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            self.stdout.write(f"Request URL: {response.url}")
            self.stdout.write(f"Status Code: {response.status_code}")
            self.stdout.write(f"Response: {response.text}")
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✅ Traccar format test PASSED"))
            else:
                self.stdout.write(self.style.ERROR("❌ Traccar format test FAILED"))
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection error: {e}"))

    def test_custom_format(self, url, lat, lng):
        """Test custom JSON format"""
        self.stdout.write("\n--- Testing Custom format ---")
        
        payload = {
            "latitude": lat,
            "longitude": lng
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            self.stdout.write(f"Status Code: {response.status_code}")
            self.stdout.write(f"Response: {response.text}")
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✅ Custom format test PASSED"))
            else:
                self.stdout.write(self.style.ERROR("❌ Custom format test FAILED"))
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection error: {e}"))

    def show_latest_location(self, journey=None):
        """Show the latest location from the database"""
        self.stdout.write("\n--- Latest Location in Database ---")
        
        if journey:
            latest = LocationUpdate.objects.filter(journey=journey).first()
        else:
            latest = LocationUpdate.objects.first()
        
        if latest:
            self.stdout.write(f"Journey: {latest.journey.title}")
            self.stdout.write(f"Latitude: {latest.latitude}")
            self.stdout.write(f"Longitude: {latest.longitude}")
            self.stdout.write(f"Timestamp: {latest.timestamp}")
            
            # Google Maps link for verification
            maps_url = f"https://www.google.com/maps?q={latest.latitude},{latest.longitude}"
            self.stdout.write(f"View on Google Maps: {maps_url}")
        else:
            self.stdout.write("No location data found in database")
            
        # Show total count
        total_count = LocationUpdate.objects.count()
        self.stdout.write(f"Total locations in database: {total_count}")

    def test_api_connectivity(self, url):
        """Test basic API connectivity"""
        test_url = url.replace('/update/', '/test/')
        
        try:
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(self.style.SUCCESS("✅ API is reachable"))
                self.stdout.write(f"Active journey: {data.get('active_journey', 'None')}")
                return True
            else:
                self.stdout.write(self.style.ERROR(f"❌ API returned status {response.status_code}"))
                return False
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Cannot reach API: {e}"))
            return False