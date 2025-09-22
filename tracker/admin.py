# tracker/admin.py

from django import forms
from django.contrib import admin

from .models import LocationUpdate
from .coordinates import format_coordinate_pair, parse_coordinate_pair


class LocationUpdateAdminForm(forms.ModelForm):
    coordinate_input = forms.CharField(
        label="Coordinates",
        help_text="Paste as (latitude, longitude) from Google Maps.",
    )

    class Meta:
        model = LocationUpdate
        fields = ("journey", "coordinate_input")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["coordinate_input"].initial = format_coordinate_pair(
                self.instance.latitude, self.instance.longitude
            )

    def clean_coordinate_input(self):
        value = self.cleaned_data.get("coordinate_input")
        parsed = parse_coordinate_pair(value)
        if not parsed:
            raise forms.ValidationError(
                "Enter coordinates in the format (latitude, longitude)."
            )

        self.cleaned_data["latitude"], self.cleaned_data["longitude"] = parsed
        return value

    def save(self, commit=True):
        instance = super().save(commit=False)
        latitude = self.cleaned_data.get("latitude")
        longitude = self.cleaned_data.get("longitude")

        if latitude is not None and longitude is not None:
            instance.latitude = latitude
            instance.longitude = longitude

        if commit:
            instance.save()
        return instance


@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    form = LocationUpdateAdminForm
    list_display = ("timestamp", "latitude", "longitude")
    readonly_fields = ("timestamp",)
    list_filter = ("timestamp",)
    date_hierarchy = "timestamp"
    fieldsets = ((None, {"fields": ("journey", "coordinate_input", "timestamp")}),)
