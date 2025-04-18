#!/usr/bin/env python3
"""
Setup script to create placeholder images for the blog application.
This script creates the media directory structure and generates two placeholder images.
"""

import os
import argparse
from PIL import Image, ImageDraw, ImageFont
import random

def create_placeholder_image(output_path, width=800, height=600, text="Placeholder"):
    """Create a placeholder image with text and random colors."""
    # Create random background color
    r = random.randint(100, 200)
    g = random.randint(100, 200)
    b = random.randint(100, 200)
    
    # Create image and drawing context
    image = Image.new('RGB', (width, height), color=(r, g, b))
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font, fall back to default if not available
    try:
        font = ImageFont.truetype("Arial", 40)
    except IOError:
        font = ImageFont.load_default()
    
    # Add text
    left, top, right, bottom = font.getbbox(text)
    text_width, text_height = right - left, bottom - top
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=(255, 255, 255), font=font)
    
    # Save the image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
    print(f"Created placeholder image: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Create placeholder images for the blog.')
    parser.add_argument('--media-dir', default='media', help='Path to the media directory')
    args = parser.parse_args()
    
    # Define image paths
    blog_images_dir = os.path.join(args.media_dir, 'blog_images')
    placeholder1 = os.path.join(blog_images_dir, 'placeholder.jpg')
    placeholder2 = os.path.join(blog_images_dir, 'placeholder2.jpg')
    
    # Create directory structure
    os.makedirs(blog_images_dir, exist_ok=True)
    
    # Create placeholder images
    create_placeholder_image(placeholder1, text="Bicycle Journey")
    create_placeholder_image(placeholder2, text="On the Road")
    
    print("Placeholder images created successfully")

if __name__ == "__main__":
    main()
