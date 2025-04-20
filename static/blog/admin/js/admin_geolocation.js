// static/admin/js/admin_geolocation.js

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("Admin geolocation script loaded");
    
    // Function to add the location button
    function addLocationButton() {
        // Find the longitude field container
        var longitudeField = document.getElementById('id_longitude');
        if (!longitudeField) {
            console.error("Longitude field not found");
            return;
        }
        
        // Create the button element
        var button = document.createElement('button');
        button.type = 'button';
        button.id = 'get-location-button';
        button.textContent = 'Get Current Location';
        button.style.margin = '10px 0';
        button.style.padding = '8px 15px';
        button.style.fontSize = '14px';
        button.style.backgroundColor = '#0078d7';
        button.style.color = 'white';
        button.style.border = 'none';
        button.style.borderRadius = '4px';
        button.style.cursor = 'pointer';
        
        // Create status span
        var statusSpan = document.createElement('span');
        statusSpan.id = 'location-status';
        statusSpan.style.marginLeft = '10px';
        
        // Create container div
        var container = document.createElement('div');
        container.className = 'form-row';
        container.appendChild(button);
        container.appendChild(statusSpan);
        
        // Add the button after the fieldset
        var fieldsets = document.querySelectorAll('fieldset');
        var locationFieldset = Array.from(fieldsets).find(function(fieldset) {
            return fieldset.querySelector('h2') && 
                  fieldset.querySelector('h2').textContent.includes('Location');
        });
        
        if (locationFieldset) {
            locationFieldset.appendChild(container);
        } else {
            // Fallback: Add after longitude field's parent div
            var longitudeParent = longitudeField.closest('.form-row');
            if (longitudeParent && longitudeParent.parentNode) {
                longitudeParent.parentNode.insertBefore(container, longitudeParent.nextSibling);
            }
        }
        
        // Add click event listener
        button.addEventListener('click', getLatestLocation);
    }
    
    // Function to get the latest location
    function getLatestLocation() {
        var button = document.getElementById('get-location-button');
        var statusSpan = document.getElementById('location-status');
        var latitudeField = document.getElementById('id_latitude');
        var longitudeField = document.getElementById('id_longitude');
        
        if (!latitudeField || !longitudeField) {
            console.error('Could not find latitude or longitude fields');
            if (statusSpan) {
                statusSpan.textContent = 'Error: Could not find form fields';
                statusSpan.style.color = 'red';
            }
            return;
        }
        
        // Disable button and show loading state
        button.disabled = true;
        button.textContent = 'Getting location...';
        
        // Get CSRF token
        var csrftoken = '';
        var csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfElement) {
            csrftoken = csrfElement.value;
        }
        
        // Create the URL
        var adminUrl = window.location.pathname.includes('/admin/') ? 
            window.location.pathname.split('/admin/')[0] + '/admin/' : 
            '/admin/';
        var apiUrl = adminUrl + 'blog/blogpost/get-latest-location/';
        
        // Make the request
        var xhr = new XMLHttpRequest();
        xhr.open('GET', apiUrl, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        if (csrftoken) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
        xhr.responseType = 'json';
        
        xhr.onload = function() {
            if (xhr.status === 200) {
                var data = xhr.response;
                console.log("Location data received:", data);
                
                if (data.success) {
                    // Update form fields
                    latitudeField.value = data.latitude;
                    longitudeField.value = data.longitude;
                    
                    // Show success message
                    statusSpan.textContent = 'Location updated successfully!';
                    statusSpan.style.color = 'green';
                    button.textContent = 'Location updated!';
                    
                    // Reset button after delay
                    setTimeout(function() {
                        button.disabled = false;
                        button.textContent = 'Get Current Location';
                        statusSpan.textContent = '';
                    }, 2000);
                } else {
                    console.error('Error getting location:', data.error);
                    statusSpan.textContent = 'Error: ' + data.error;
                    statusSpan.style.color = 'red';
                    button.textContent = 'Error';
                    
                    // Reset button after delay
                    setTimeout(function() {
                        button.disabled = false;
                        button.textContent = 'Get Current Location';
                    }, 2000);
                }
            } else {
                console.error('XHR error:', xhr.statusText);
                statusSpan.textContent = 'Error connecting to server';
                statusSpan.style.color = 'red';
                button.textContent = 'Error';
                
                // Reset button after delay
                setTimeout(function() {
                    button.disabled = false;
                    button.textContent = 'Get Current Location';
                    statusSpan.textContent = '';
                }, 2000);
            }
        };
        
        xhr.onerror = function() {
            console.error('Network error');
            statusSpan.textContent = 'Network error';
            statusSpan.style.color = 'red';
            button.textContent = 'Error';
            
            // Reset button after delay
            setTimeout(function() {
                button.disabled = false;
                button.textContent = 'Get Current Location';
                statusSpan.textContent = '';
            }, 2000);
        };
        
        xhr.send();
    }
    
    // Initialize by adding the button
    addLocationButton();
});