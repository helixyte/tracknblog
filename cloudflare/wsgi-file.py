# wsgi.py
import os
import sys

# Add the project directory to the system path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicycle_blog.settings')

# Import and use Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
