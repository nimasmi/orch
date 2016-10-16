from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsnippets.models import register_snippet


@register_snippet
class Category(models.Model):
    name = models.TextField()

    panels = [
        FieldPanel('name', classname="full"),
    ]

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
