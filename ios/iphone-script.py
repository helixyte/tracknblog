# location_sender.py
# Script for Pythonista iOS app to send location to the server
import requests
import json
import time
import location
import console

# URL of your Django server with the correct path
SERVER_URL = "https://vista-grande.net/blog/tracker/update/"

def send_location():
    try:
        # Request location permission and start updating
        location.start_updates()
        
        # Give it some time to get an accurate reading
        time.sleep(2)
        
        # Get the current location
        loc = location.get_location()
        
        # Extract coordinates
        lat = loc.get('latitude')
        lng = loc.get('longitude')
        
        # Create the data payload
        data = {
            'latitude': lat,
            'longitude': lng
        }
        
        # Send the data to the server
        response = requests.post(
            SERVER_URL,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        
        # Check the response
        if response.status_code == 200:
            console.alert('Success', 'Location updated successfully', 'OK')
        else:
            console.alert('Error', f'Failed to update location: {response.text}', 'OK')
    
    except Exception as e:
        console.alert('Error', f'An error occurred: {str(e)}', 'OK')
    
    finally:
        # Stop updating location to save battery
        location.stop_updates()

# Run the function when the script is executed
if __name__ == '__main__':
    send_location()
