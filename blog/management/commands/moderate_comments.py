# blog/management/commands/moderate_comments.py
from django.core.management.base import BaseCommand, CommandError
from blog.models import Comment
from django.utils import timezone
from datetime import timedelta
import re

class Command(BaseCommand):
    help = 'Moderate comments based on various criteria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--approve-all',
            action='store_true',
            help='Approve all unapproved comments',
        )
        parser.add_argument(
            '--auto-moderate',
            action='store_true',
            help='Apply automated moderation rules to all unapproved comments',
        )
        parser.add_argument(
            '--delete-spam',
            action='store_true',
            help='Delete all comments marked as spam',
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Only process comments from the last X days',
        )

    def handle(self, *args, **options):
        # Get comments to process
        comments = Comment.objects.all()
        
        # Filter by date if specified
        if options['days']:
            cutoff_date = timezone.now() - timedelta(days=options['days'])
            comments = comments.filter(created_at__gte=cutoff_date)
            self.stdout.write(f"Processing comments from the last {options['days']} days")
            
        # Approve all comments
        if options['approve_all']:
            unapproved = comments.filter(approved=False)
            count = unapproved.count()
            unapproved.update(approved=True)
            self.stdout.write(self.style.SUCCESS(f'Successfully approved {count} comments'))
            
        # Auto-moderate comments
        if options['auto_moderate']:
            unapproved = comments.filter(approved=False)
            approved_count = 0
            
            for comment in unapproved:
                if self._should_approve(comment):
                    comment.approved = True
                    comment.save()
                    approved_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'Auto-moderation complete: {approved_count} comments approved, '
                f'{unapproved.count() - approved_count} remain unapproved'
            ))
            
        # Delete spam
        if options['delete_spam']:
            spam_count = comments.filter(approved=False).count()
            comments.filter(approved=False).delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {spam_count} spam comments'))
    
    def _should_approve(self, comment):
        """Apply moderation rules to determine if a comment should be approved"""
        # Check for too many links (common spam characteristic)
        url_pattern = re.compile(r'https?://\S+')
        urls = url_pattern.findall(comment.content)
        if len(urls) > 2:
            return False
            
        # Check for very short comments (might be spam)
        if len(comment.content.strip()) < 5:
            return False
            
        # Check for common spam phrases
        spam_phrases = [
            'viagra', 'cialis', 'casino', 'pharmacy', 'loan', 'free money',
            'weight loss', 'xxx', 'porn', 'click here'
        ]
        content_lower = comment.content.lower()
        for phrase in spam_phrases:
            if phrase in content_lower:
                return False
                
        # Comment passed all checks, should be approved
        return True