# blog/migrations/xxxx_populate_initial_journey.py
from django.db import migrations, transaction
from django.utils import timezone

def create_initial_journey(apps, schema_editor):
    Journey = apps.get_model('blog', 'Journey')
    BlogPost = apps.get_model('blog', 'BlogPost')
    LocationUpdate = apps.get_model('tracker', 'LocationUpdate')
    
    # Skip if no blog posts exist
    if not BlogPost.objects.exists():
        return
    
    # Create the initial journey based on existing data
    with transaction.atomic():
        # Get earliest blog post date for start_date
        start_date = BlogPost.objects.order_by('timestamp').first().timestamp.date()
        
        # Create the initial journey
        initial_journey = Journey.objects.create(
            title="Cycling East",
            slug="cycling-east",
            description="My first bicycle journey heading eastward.",
            start_date=start_date,
            is_active=True
        )
        
        # Assign all blog posts to this journey
        BlogPost.objects.update(journey=initial_journey)
        
        # Assign all location updates to this journey
        LocationUpdate.objects.update(journey=initial_journey)

def reverse_migration(apps, schema_editor):
    # No need to reverse this operation as the field will be dropped
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_create_journey_model'),  # Make sure to use the correct migration name
        ('tracker', '0002_add_journey_to_locationupdate'),  # Make sure to use the correct migration name
    ]

    operations = [
        migrations.RunPython(create_initial_journey, reverse_migration),
    ]