from django.core.exceptions import ValidationError
from django.db import models

import requests
from geopy.geocoders import Nominatim
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailsnippets.models import register_snippet


@register_snippet
class Location(models.Model):
    title = models.CharField(max_length=255)
    # phone
    landline_telephone = models.CharField(max_length=255, blank=True)
    mobile_telephone = models.CharField(max_length=255, blank=True)
    # address
    address_line_one = models.CharField(max_length=255, blank=True)
    address_line_two = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    county_or_state = models.CharField(max_length=255, blank=True)
    zip_or_postal_code = models.CharField(max_length=255, blank=True)
    # lat/lon
    latitude = models.FloatField(editable=False, null=True)
    longitude = models.FloatField(editable=False, null=True)

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            [
                FieldPanel('landline_telephone'),
                FieldPanel('mobile_telephone'),
            ],
            heading="Phone numbers",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('address_line_one'),
                FieldPanel('address_line_two'),
                FieldPanel('city'),
                FieldPanel('county_or_state'),
                FieldPanel('zip_or_postal_code'),
            ],
            heading="Address",
            classname="collapsible"
        ),
    ]

    def clean(self):
        geolocator = Nominatim()
        try:
            location_string = "%s %s %s %s %s" % (
                self.address_line_one, self.address_line_two, self.city, self.county_or_state, self.zip_or_postal_code
            )
            location = geolocator.geocode(location_string, exactly_one=True)
        except Exception as e:
            raise ValidationError({
                'address_line_one': e
            })

        self.latitude = None
        self.longitude = None
        if location:
            self.latitude = location.latitude
            self.longitude = location.longitude
        else:
            raise ValidationError({
                'address_line_one':
                'Unable to find coordinates for the given location: {}. Try using different or fewer fields.'.format(location_string)
            })

    def __str__(self):
        return self.title
