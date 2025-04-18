#!/usr/bin/env python3
"""
Script to download all the bicycle blog project artifacts.
Run this from the root of your git repository.
"""
import os
import sys

# Dictionary mapping artifact IDs to file paths
ARTIFACTS = {
    # Models
    "tracker-models": "tracker/models.py",
    "blog-models": "blog/models.py",
    
    # Views
    "tracker-views": "tracker/views.py",
    "blog-views": "blog/views.py",
    
    # URLs
    "project-urls": "bicycle_blog/urls.py",
    "tracker-urls": "tracker/urls.py",
    "blog-urls": "blog/urls.py",
    
    # Templates
    "base-template": "templates/base.html",
    "blog-list-template": "templates/blog/blog_list.html",
    "blog-detail-template": "templates/blog/blog_detail.html",
    
    # Admin
    "blog-admin": "blog/admin.py",
    "tracker-admin": "tracker/admin.py",
    
    # Settings
    "project-settings": "bicycle_blog/settings.py",
    "updated-settings": "bicycle_blog/settings_updates.py",
    "context-processor": "bicycle_blog/context_processors.py",
    "cloudflare-settings": "bicycle_blog/cloudflare_settings.py",
    
    # iOS scripts
    "iphone-script": "ios/location_sender.py",
    "updated-iphone-script": "ios/updated_location_sender.py",
    
    # Deployment
    "deployment-guide": "docs/deployment_guide.md",
    "ios-shortcut-guide": "docs/ios_shortcut_guide.md",
    "cloudflare-setup-guide": "docs/cloudflare_setup_guide.md",
    
    # Cloudflare
    "wsgi-file": "bicycle_blog/wsgi.py",
    "cloudflare-worker": "cloudflare/worker.js",
    
    # Updated templates
    "updated-base-template": "templates/updated_base.html",
    "updated-blog-list": "templates/blog/updated_blog_list.html",
    "updated-blog-detail": "templates/blog/updated_blog_detail.html",
    
    # Project structure
    "requirements-file": "requirements.txt",
    "project-structure": "docs/project_structure.md",
}

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = {
        "bicycle_blog",
        "blog",
        "tracker",
        "templates",
        "templates/blog",
        "ios",
        "docs",
        "cloudflare",
    }
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main function to run the script."""
    print("Creating project directories...")
    create_directories()
    
    print("Now that directories are created, you need to manually copy content from each artifact")
    print("to the corresponding file. Copy the content of each artifact shown above and save")
    print("it to the file path listed.")
    
    print("\nHere's the list of files to create:")
    for artifact_id, file_path in ARTIFACTS.items():
        print(f"- {artifact_id} -> {file_path}")
        
    print("\nAfter copying all files, run these commands to commit them to your git repository:")
    print("git add .")
    print("git commit -m \"Add initial bicycle blog project files\"")

if __name__ == "__main__":
    main()
