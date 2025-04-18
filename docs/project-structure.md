# Bicycle Blog Project Structure

```
bicycle_blog/
├── bicycle_blog/               # Project directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Main settings file
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py
├── blog/                       # Blog app
│   ├── __init__.py
│   ├── admin.py                # Admin configuration for blog
│   ├── apps.py
│   ├── migrations/
│   ├── models.py               # Blog models (BlogPost, BlogImage)
│   ├── tests.py
│   ├── urls.py                 # Blog URL routes
│   └── views.py                # Blog views
├── tracker/                    # Location tracking app
│   ├── __init__.py
│   ├── admin.py                # Admin configuration for tracker
│   ├── apps.py
│   ├── migrations/
│   ├── models.py               # Location model
│   ├── tests.py
│   ├── urls.py                 # Tracker API endpoints
│   └── views.py                # Tracker API views
├── templates/                  # HTML templates
│   ├── base.html               # Base template with common elements
│   └── blog/
│       ├── blog_list.html      # List of blog posts with map
│       └── blog_detail.html    # Single blog post with image slider
├── media/                      # Uploaded media (created during runtime)
│   └── blog_images/            # Blog post images
├── static/                     # Static files
├── manage.py                  
└── requirements.txt            # Project dependencies
```

This structure follows Django best practices with:

1. Separate apps for different functionalities:
   - `blog` app for blog posts and images
   - `tracker` app for location tracking

2. Templates organized by app, with a base template

3. Clean separation of concerns:
   - Models define data structure
   - Views handle business logic
   - Templates handle presentation
   - URLs define routing
