# tracker/migrations/xxxx_add_journey_to_locationupdate.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_create_journey_model'),  # Make sure to use the correct migration name
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationupdate',
            name='journey',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='locations',
                to='blog.journey',
                # Initially set to null, but will be populated in data migration
                null=True,
            ),
        ),
    ]