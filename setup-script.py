#!/usr/bin/env python3
"""
Setup script for the bicycle blog application.
This script:
1. Creates the SQLite database
2. Runs migrations
3. Creates a superuser
4. Sets up placeholder images
5. Creates sample data
"""

import os
import sys
import subprocess
import argparse

def run_command(command, description):
    """Run a shell command and print its output."""
    print(f"\n---- {description} ----")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"Error: {result.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Set up the bicycle blog database and sample data.')
    parser.add_argument('--username', default='admin', help='Admin username')
    parser.add_argument('--password', default='biketrip2023', help='Admin password')
    parser.add_argument('--email', default='admin@example.com', help='Admin email')
    parser.add_argument('--no-sample-data', action='store_true', help='Skip sample data creation')
    args = parser.parse_args()
    
    # Make sure we're in the project root directory
    if not os.path.exists('manage.py'):
        print("Error: This script must be run from the project root directory (where manage.py is located)")
        sys.exit(1)
    
    # Step 1: Make migrations
    if not run_command('python manage.py makemigrations', 'Creating migrations'):
        sys.exit(1)
    
    # Step 2: Apply migrations
    if not run_command('python manage.py migrate', 'Applying migrations'):
        sys.exit(1)
    
    # Step 3: Set up placeholder images
    if not run_command('python setup_placeholders.py', 'Creating placeholder images'):
        print("Warning: Failed to create placeholder images. Continuing anyway...")
    
    # Step 4: Initialize the database with admin user and optionally sample data
    sample_data_flag = '' if args.no_sample_data else '--sample-data'
    init_command = f'python manage.py init_db --username={args.username} --password={args.password} --email={args.email} {sample_data_flag}'
    if not run_command(init_command, 'Initializing database'):
        sys.exit(1)
    
    print("\n---- Setup Complete ----")
    print(f"Admin user created with username: {args.username} and password: {args.password}")
    print("You can now start the development server with: python manage.py runserver")
    print("Access the admin interface at: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main()
