# blog/migrations/xxxx_make_journey_fields_required.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_populate_initial_journey'),  # Make sure to use the correct migration name
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='journey',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='posts',
                to='blog.journey',
            ),
        ),
    ]