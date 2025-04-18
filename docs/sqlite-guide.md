# SQLite Database Management for Your Bicycle Blog

This guide covers everything you need to know about managing the SQLite database for your bicycle blog project.

## Table of Contents
1. [Introduction to SQLite](#introduction-to-sqlite)
2. [Database Setup](#database-setup)
3. [Basic Database Operations](#basic-database-operations)
4. [Backing Up Your Database](#backing-up-your-database)
5. [Database Migration](#database-migration)
6. [Troubleshooting](#troubleshooting)
7. [Database Performance](#database-performance)

## Introduction to SQLite

SQLite is a self-contained, serverless, zero-configuration, transactional SQL database engine. It's an excellent choice for your bicycle blog project because:

- **No separate server process** - Perfect for a personal blog
- **Zero configuration** - Works out of the box
- **Cross-platform** - Works on all operating systems
- **Reliable** - ACID-compliant, even after system crashes
- **Portable** - The entire database is stored in a single file

## Database Setup

The Django project is already configured to use SQLite. Here's how to set up your database:

1. **Run migrations to create the database schema**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create a superuser for the admin interface**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Use the provided setup script for a complete setup**:
   ```bash
   python setup.py --username=admin --password=yourpassword --email=your@email.com
   ```

4. **To include sample data**:
   ```bash
   python setup.py --username=admin --password=yourpassword --email=your@email.com
   ```

5. **To skip sample data**:
   ```bash
   python setup.py --username=admin --password=yourpassword --email=your@email.com --no-sample-data
   ```

## Basic Database Operations

### Accessing the Database from Django

Django provides a convenient ORM (Object-Relational Mapper) to interact with the database:

```python
# Get all blog posts
from blog.models import BlogPost
all_posts = BlogPost.objects.all()

# Get the latest blog post
latest_post = BlogPost.objects.latest('timestamp')

# Get the latest location
from tracker.models import LocationUpdate
latest_location = LocationUpdate.objects.latest('timestamp')
```

### Using the Django Shell

The Django shell provides a convenient way to interact with your database:

```bash
python manage.py shell
```

### Direct SQLite Access

You can also access the SQLite database directly:

```bash
sqlite3 db.sqlite3
```

Common SQLite commands:
```sql
-- Show all tables
.tables

-- View schema for a table
.schema blog_blogpost

-- Run a query
SELECT * FROM blog_blogpost ORDER BY timestamp DESC LIMIT 5;

-- Exit SQLite
.exit
```

## Backing Up Your Database

SQLite databases are single files, making backups simple:

1. **Simple file copy**:
   ```bash
   cp db.sqlite3 db.sqlite3.backup
   ```

2. **Using SQLite's dump command**:
   ```bash
   sqlite3 db.sqlite3 .dump > backup.sql
   ```

3. **Restore from SQL dump**:
   ```bash
   sqlite3 db.sqlite3.new < backup.sql
   ```

4. **Automated backup script**:
   ```bash
   # Create this as backup.sh
   #!/bin/bash
   BACKUP_DIR="backups"
   mkdir -p $BACKUP_DIR
   TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
   sqlite3 db.sqlite3 .dump > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
   ```

## Database Migration

As your project evolves, you'll need to update your database schema:

1. **Create migrations after modifying models**:
   ```bash
   python manage.py makemigrations
   ```

2. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

3. **View migration status**:
   ```bash
   python manage.py showmigrations
   ```

4. **When deploying to production**:
   - Always back up the database before migration
   - Test migrations on a copy of the production data first

## Troubleshooting

### Common Issues and Solutions

1. **Database is locked**:
   - This usually happens when multiple processes try to write to the database
   - Ensure all other connections to the database are closed
   - Restart the Django development server

2. **No such table**:
   - Run migrations: `python manage.py migrate`
   - Check if your app is in INSTALLED_APPS in settings.py

3. **Corrupt database**:
   - Restore from backup
   - If no backup is available, try: `sqlite3 db.sqlite3 "PRAGMA integrity_check;"`

### Database Integrity Check

```bash
sqlite3 db.sqlite3 "PRAGMA integrity_check;"
```

## Database Performance

For most personal blog sites, SQLite performance is more than adequate. However, as your blog grows:

1. **Add indexes to frequently queried fields**:
   ```python
   # In your models.py
   class BlogPost(models.Model):
       # ...
       class Meta:
           indexes = [
               models.Index(fields=['timestamp']),
           ]
   ```

2. **Consider database optimizations**:
   ```bash
   sqlite3 db.sqlite3 "VACUUM;"
   ```

3. **Monitor database size**:
   ```bash
   ls -lh db.sqlite3
   ```

4. **If database exceeds 100MB or has high concurrent write loads**:
   - Consider migrating to PostgreSQL for better performance

Remember, for a personal bicycle trip blog, SQLite should be more than capable of handling your needs. It's only when you have many concurrent users or very large datasets that you might need to consider alternatives.
