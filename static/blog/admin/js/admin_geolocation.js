// static/blog/admin/js/admin_geolocation.js

// Utility helpers
function getAdminLocationElements() {
    var coordinateField = document.getElementById('id_coordinate_input');

    if (!coordinateField) {
        console.error('Coordinate field not found in the admin form.');
        return null;
    }

    var button = document.getElementById('get-location-button');
    var statusSpan = document.getElementById('location-status');

    if (!button) {
        // Create button when it does not already exist in the template
        button = document.createElement('button');
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

        var container = document.createElement('div');
        container.className = 'form-row';
        container.appendChild(button);

        var coordinateParent = coordinateField.closest('.form-row');
        if (coordinateParent && coordinateParent.parentNode) {
            coordinateParent.parentNode.insertBefore(container, coordinateParent.nextSibling);
        } else {
            coordinateField.parentNode.appendChild(container);
        }
    }

    if (!statusSpan) {
        statusSpan = document.createElement('span');
        statusSpan.id = 'location-status';
        statusSpan.style.marginLeft = '10px';
        button.insertAdjacentElement('afterend', statusSpan);
    }

    return {
        button: button,
        statusSpan: statusSpan,
        coordinateField: coordinateField
    };
}

function setStatus(statusSpan, message, color) {
    if (!statusSpan) {
        return;
    }
    statusSpan.textContent = message || '';
    if (color) {
        statusSpan.style.color = color;
    }
}

function resetButtonState(button, statusSpan) {
    if (!button) {
        return;
    }
    button.disabled = false;
    button.textContent = 'Get Current Location';
    setStatus(statusSpan, '');
}

function applyCoordinates(coordinateField, latitude, longitude) {
    var lat = typeof latitude === 'string' ? parseFloat(latitude) : latitude;
    var lng = typeof longitude === 'string' ? parseFloat(longitude) : longitude;

    if (!isFinite(lat) || !isFinite(lng)) {
        throw new Error('Invalid coordinates returned.');
    }

    coordinateField.value = '(' + lat.toFixed(6) + ', ' + lng.toFixed(6) + ')';
}

function getJourneyId() {
    var journeyField = document.getElementById('id_journey');
    return journeyField && journeyField.value ? journeyField.value : '';
}

function buildAdminApiUrl() {
    var baseAdminPath = '/admin/';
    if (window.location.pathname.includes('/admin/')) {
        baseAdminPath = window.location.pathname.split('/admin/')[0] + '/admin/';
    }
    var url = baseAdminPath + 'blog/blogpost/get-latest-location/';
    var journeyId = getJourneyId();
    if (journeyId) {
        url += '?journey_id=' + encodeURIComponent(journeyId);
    }
    return url;
}

function fetchLatestLocationFromServer() {
    return new Promise(function(resolve, reject) {
        var csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
        var headers = {
            'X-Requested-With': 'XMLHttpRequest'
        };
        if (csrfElement && csrfElement.value) {
            headers['X-CSRFToken'] = csrfElement.value;
        }

        fetch(buildAdminApiUrl(), {
            method: 'GET',
            headers: headers,
            credentials: 'same-origin'
        })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Server responded with status ' + response.status);
                }
                return response.json();
            })
            .then(function(data) {
                var hasLatitude = typeof data.latitude !== 'undefined' && data.latitude !== null;
                var hasLongitude = typeof data.longitude !== 'undefined' && data.longitude !== null;
                if (data.success && hasLatitude && hasLongitude) {
                    resolve(data);
                } else {
                    throw new Error(data.error || 'No location data available.');
                }
            })
            .catch(function(error) {
                reject(error);
            });
    });
}

function requestBrowserGeolocation() {
    return new Promise(function(resolve, reject) {
        if (!('geolocation' in navigator)) {
            reject(new Error('Geolocation is not supported by this browser.'));
            return;
        }

        var isLocalhost = /^localhost$|^127\.0\.0\.1$/.test(window.location.hostname);
        if (!window.isSecureContext && !isLocalhost) {
            reject(new Error('Browser location requires HTTPS.'));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function(position) {
                resolve(position);
            },
            function(error) {
                var message = error.message || 'Unable to retrieve location.';
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        message = 'Permission to access location was denied.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = 'Location information is unavailable.';
                        break;
                    case error.TIMEOUT:
                        message = 'Timed out while retrieving location.';
                        break;
                    default:
                        if (message.toLowerCase().includes('secure origin')) {
                            message = 'Browser blocked location because the connection is not secure.';
                        }
                        break;
                }
                reject(new Error(message));
            },
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            }
        );
    });
}

async function handleLocationRequest(elements) {
    var button = elements.button;
    var statusSpan = elements.statusSpan;
    var coordinateField = elements.coordinateField;

    button.disabled = true;
    button.textContent = 'Getting location...';
    setStatus(statusSpan, 'Requesting device location…', '#2563eb');

    try {
        var position = await requestBrowserGeolocation();
        var coords = position.coords;
        applyCoordinates(coordinateField, coords.latitude, coords.longitude);

        var accuracyMessage = typeof coords.accuracy === 'number'
            ? ' (±' + Math.round(coords.accuracy) + 'm accuracy)'
            : '';
        setStatus(statusSpan, 'Location updated from this device' + accuracyMessage + '.', 'green');
        button.textContent = 'Location updated!';
        setTimeout(function() {
            resetButtonState(button, statusSpan);
        }, 2500);
        return;
    } catch (browserError) {
        console.warn('Browser geolocation failed:', browserError);
        setStatus(statusSpan, browserError.message + ' Trying latest tracker update…', '#d97706');
    }

    try {
        var data = await fetchLatestLocationFromServer();
        applyCoordinates(coordinateField, data.latitude, data.longitude);

        var timestampMessage = '';
        if (data.timestamp) {
            try {
                var timestamp = new Date(data.timestamp);
                if (!isNaN(timestamp.getTime())) {
                    timestampMessage = ' from ' + timestamp.toLocaleString();
                }
            } catch (err) {
                // Ignore parsing errors and leave timestampMessage empty
            }
        }

        setStatus(statusSpan, 'Using latest tracker update' + timestampMessage + '.', 'green');
        button.textContent = 'Location updated!';
        setTimeout(function() {
            resetButtonState(button, statusSpan);
        }, 2500);
    } catch (serverError) {
        console.error('Failed to fetch latest tracker location:', serverError);
        setStatus(statusSpan, serverError.message || 'Unable to fetch location.', 'red');
        button.textContent = 'Error';
        setTimeout(function() {
            resetButtonState(button, statusSpan);
        }, 3000);
    }
}

function initializeLocationButton() {
    var elements = getAdminLocationElements();
    if (!elements) {
        return;
    }

    // Remove existing listeners by cloning if necessary to avoid duplicates
    var originalButton = elements.button;
    var clonedButton = originalButton.cloneNode(true);
    if (originalButton.parentNode) {
        originalButton.parentNode.replaceChild(clonedButton, originalButton);
        elements.button = clonedButton;
        if (elements.statusSpan) {
            elements.button.insertAdjacentElement('afterend', elements.statusSpan);
        }
    }

    elements.button.addEventListener('click', function(event) {
        event.preventDefault();
        handleLocationRequest(elements);
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeLocationButton);
} else {
    initializeLocationButton();
}
