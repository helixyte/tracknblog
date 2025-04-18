# Setting Up iPhone Location Tracking

To continuously track your location and send updates to your blog, we'll use iOS Shortcuts with automation. This approach doesn't require any additional apps beyond the built-in Shortcuts app.

## Creating the Location Update Shortcut

1. Open the Shortcuts app on your iPhone
2. Tap the "+" button to create a new shortcut
3. Tap "Add Action"
4. Search for "Get Current Location" and add it
5. Add the "URL" action and enter your server URL: `https://yourdomain.com/tracker/update/`
6. Add the "Get Contents of URL" action with these settings:
   - Method: POST
   - Request Body: JSON
   - Add two key-value pairs:
     - Key: latitude, Value: Shortcut Input → Location → Latitude
     - Key: longitude, Value: Shortcut Input → Location → Longitude
7. Optionally, add a "Notification" action to confirm updates (can be disabled later)
8. Name your shortcut "Update Bike Location" and save it

## Setting Up Automation

To run this shortcut automatically at regular intervals:

1. Go to the "Automation" tab in the Shortcuts app
2. Tap the "+" button to create a new automation
3. Choose "Time of Day"
4. Set it to repeat every hour (or your preferred interval)
5. Tap "Next"
6. Add the "Run Shortcut" action
7. Select your "Update Bike Location" shortcut
8. Tap "Next"
9. **Important**: Toggle OFF "Ask Before Running" to make it run automatically
10. Tap "Done"

## Battery Considerations

Continuous location tracking can drain your battery. To manage this:

1. In your shortcut, adjust the "Get Current Location" action:
   - Tap on it to see options
   - Set accuracy to "Reduced" to save battery

2. Consider creating two automations:
   - One that runs more frequently when you're moving (e.g., every 10-15 minutes)
   - Another that runs less frequently when you're stationary (e.g., every hour)
   
3. For longer battery life, you might consider using a dedicated GPS tracker device instead of your iPhone.

## Alternative: Use a Dedicated App

If you want more reliable background location tracking, consider these apps:

1. **Overland** - Open-source GPS tracker that can send to custom endpoints
2. **Traccar Client** - Free GPS tracking client that works with your server
3. **GPS Logger for iOS** - Can log and send GPS coordinates to a server

These apps are designed to run in the background and send periodic updates while minimizing battery impact.
