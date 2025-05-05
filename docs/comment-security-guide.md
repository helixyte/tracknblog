# Comment Security Features Guide

This guide explains how to use the security features implemented for your blog's comment system.

## Features Overview

1. **Honeypot Field**: A hidden field that catches bot submissions
2. **Comment Moderation**: Tools to approve/reject comments based on content
3. **Rate Limiting**: Prevents users from submitting too many comments in a short period

## Configuration

### Honeypot Field

The honeypot field is automatically included in the comment form. It's a hidden field called "website" that humans won't see or fill out, but bots will. If the field is filled, the submission is rejected silently.

No configuration is needed for this feature.

### Comment Moderation

You can configure comment moderation in `tracnblog/settings.py`:

```python
# Enable/disable automatic moderation for all comments
AUTO_MODERATE_COMMENTS = False  # Set to True to require approval for all comments

# Keywords that trigger automatic moderation
COMMENT_MODERATION_KEYWORDS = [
    'viagra', 'cialis', 'casino', 'pharmacy', 'loan', 'free money',
    'weight loss', 'xxx', 'porn', 'href=', 'http://', 'https://'
]
```

#### Admin Interface

The admin interface has been enhanced for easier comment moderation:

1. Go to Admin → Blog → Comments
2. You'll see a list of all comments with approval status
3. Use the checkboxes to select comments, then use the dropdown to:
   - Approve comments
   - Disapprove comments
   - Mark as spam

#### Management Command

You can also moderate comments via the command line:

```bash
# Approve all pending comments
python manage.py moderate_comments --approve-all

# Apply auto-moderation rules
python manage.py moderate_comments --auto-moderate

# Delete all unapproved comments
python manage.py moderate_comments --delete-spam

# Only process recent comments
python manage.py moderate_comments --auto-moderate --days=7
```

### Rate Limiting

Rate limiting prevents abuse by limiting how frequently users can post comments. Configure it in `settings.py`:

```python
# Time window in seconds
COMMENT_RATE_LIMIT_TIME = 300  # 5 minutes

# Maximum comments per time window
COMMENT_RATE_LIMIT_COUNT = 3   # Max 3 comments per 5 minutes
```

## How It Works

### Honeypot Field

1. Bots automatically fill out all form fields, including the hidden honeypot field
2. Real users don't see or fill out the honeypot field
3. If the honeypot field contains any text, the submission is silently rejected

### Comment Moderation

1. Comments are checked against moderation keywords
2. If AUTO_MODERATE_COMMENTS is True, all comments require manual approval
3. Unapproved comments are stored in the database but not displayed on the site
4. Admins can review and approve/reject comments through the admin interface

### Rate Limiting

1. When a user submits a comment, their IP address is recorded
2. If the same IP submits too many comments in the specified time window, additional submissions are blocked
3. This prevents flooding the site with spam or abusive comments

## Security Best Practices

1. **Regularly review comments**: Check the admin panel for pending comments
2. **Update keyword list**: Add new spam keywords as they appear
3. **Adjust rate limits**: Tighten or loosen based on your traffic patterns
4. **Run moderation command**: Schedule the moderation command to run daily

## Troubleshooting

- **Legitimate comments getting flagged**: Check and adjust your moderation keywords
- **Too many spam comments getting through**: Decrease rate limits or add more keywords
- **Users complaining about rate limiting**: Increase the rate limit threshold

## Command Reference

```bash
# View all comment moderation options
python manage.py moderate_comments --help
```
