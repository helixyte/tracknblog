# tracker/migrations/xxxx_make_journey_field_required.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', 'xxxx_make_journey_fields_required'),  # Make sure to use the correct migration name
        ('tracker', 'xxxx_add_journey_to_locationupdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationupdate',
            name='journey',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='locations',
                to='blog.journey',
            ),
        ),
    ]