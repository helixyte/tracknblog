# blog/management/commands/create_journey.py
from django.core.management.base import BaseCommand, CommandError
from blog.models import Journey
from django.utils import timezone
from django.utils.text import slugify
import datetime

class Command(BaseCommand):
    help = 'Create a new journey for the cycling blog'

    def add_arguments(self, parser):
        parser.add_argument('title', type=str, help='Title of the journey')
        parser.add_argument('description', type=str, help='Description of the journey')
        parser.add_argument('--start-date', type=str, help='Start date in YYYY-MM-DD format (defaults to today)')
        parser.add_argument('--make-active', action='store_true', help='Make this the active journey')
        parser.add_argument('--slug', type=str, help='Custom slug for the journey (defaults to slugified title)')

    def handle(self, *args, **options):
        title = options['title']
        description = options['description']
        
        # Handle start date
        if options['start_date']:
            try:
                start_date = datetime.datetime.strptime(options['start_date'], '%Y-%m-%d').date()
            except ValueError:
                raise CommandError('Start date must be in YYYY-MM-DD format')
        else:
            start_date = timezone.now().date()
            
        # Handle slug
        slug = options.get('slug', None) or slugify(title)
        
        # Check if slug already exists
        if Journey.objects.filter(slug=slug).exists():
            raise CommandError(f'A journey with slug "{slug}" already exists. Please use a different title or specify a custom slug.')
        
        # Create the journey
        journey = Journey(
            title=title,
            description=description,
            start_date=start_date,
            slug=slug,
            is_active=options['make_active']
        )
        
        # If making active, deactivate other journeys
        if options['make_active']:
            Journey.objects.all().update(is_active=False)
        
        # Save the journey
        journey.save()
        
        self.stdout.write(self.style.SUCCESS(f'Journey "{title}" created successfully!'))
        self.stdout.write(f'Slug: {journey.slug}')
        self.stdout.write(f'Start date: {journey.start_date}')
        self.stdout.write(f'Active: {journey.is_active}')