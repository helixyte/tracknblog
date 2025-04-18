# Deployment Guide for Your Bicycle Blog

This guide will help you deploy your Django-based bicycle blog on PythonAnywhere, a platform that makes it easy to host Python web applications.

## Prerequisites

1. Create a [PythonAnywhere account](https://www.pythonanywhere.com/registration/register/beginner/)
2. Have your blog code in a GitHub repository

## Step 1: Set Up a Web App on PythonAnywhere

1. Log in to your PythonAnywhere account
2. Click on the "Web" tab
3. Click "Add a new web app"
4. Choose "Manual configuration"
5. Select Python 3.10 (or the latest available version)

## Step 2: Clone Your Repository

1. Click on the "Consoles" tab
2. Start a new Bash console
3. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/bicycle_blog.git
   ```

## Step 3: Set Up a Virtual Environment

1. Create a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 bicycle_blog_env
   ```
2. Install your dependencies:
   ```bash
   cd bicycle_blog
   pip install -r requirements.txt
   ```
   (Make sure to create a requirements.txt before deploying)

## Step 4: Configure Your Web App

1. Go back to the "Web" tab
2. In the "Code" section:
   - Set "Source code" to `/home/yourusername/bicycle_blog`
   - Set "Working directory" to `/home/yourusername/bicycle_blog`
   - Set "WSGI configuration file" - Click on the link and edit it according to the template below

3. In the "Virtualenv" section:
   - Enter the path to your virtualenv: `/home/yourusername/.virtualenvs/bicycle_blog_env`

4. Click "Save" at the top of the page

## Step 5: Configure WSGI File

Edit the WSGI file to include:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/bicycle_blog'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'bicycle_blog.settings'

# Serve Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Step 6: Set Up Static and Media Files

1. Create static directories:
   ```bash
   mkdir -p /home/yourusername/bicycle_blog/static
   mkdir -p /home/yourusername/bicycle_blog/media
   ```

2. Go back to the "Web" tab
3. In the "Static files" section, add:
   - URL: `/static/` - Directory: `/home/yourusername/bicycle_blog/static/`
   - URL: `/media/` - Directory: `/home/yourusername/bicycle_blog/media/`

4. Click "Save"

## Step 7: Configure Your Settings

Create a file called `local_settings.py` in your project directory:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

# Database settings (using the default SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/yourusername/bicycle_blog/db.sqlite3',
    }
}

# Static files settings
STATIC_ROOT = '/home/yourusername/bicycle_blog/static'
MEDIA_ROOT = '/home/yourusername/bicycle_blog/media'
```

Import these settings in your main `settings.py`:

```python
try:
    from .local_settings import *
except ImportError:
    pass
```

## Step 8: Set Up the Database

Run migrations to set up your database:

```bash
cd ~/bicycle_blog
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

## Step 9: Collect Static Files

```bash
python manage.py collectstatic
```

## Step 10: Restart Your Web App

1. Go back to the "Web" tab
2. Click the "Reload" button

Your website should now be available at `yourusername.pythonanywhere.com`.

## Updating Your App

When you want to update your app:

1. Pull the latest changes from GitHub:
   ```bash
   cd ~/bicycle_blog
   git pull
   ```

2. Install any new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations if needed:
   ```bash
   python manage.py migrate
   ```

4. Collect static files if needed:
   ```bash
   python manage.py collectstatic
   ```

5. Reload your web app from the "Web" tab

## Setting Up Domain Name (Optional)

If you want to use a custom domain name (like `goingeast.com`):

1. Register a domain name
2. In the "Web" tab, go to the "Domains" section
3. Add your domain name
4. Configure your domain's DNS settings to point to PythonAnywhere (follow their instructions)