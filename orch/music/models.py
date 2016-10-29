from __future__ import unicode_literals

from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet


@register_snippet
class Composer(models.Model):
    name = models.CharField(
        "Full name", max_length=100, help_text='Including surname')
    short_name = models.CharField(
        "Short name", max_length=100,
        help_text="Surname only or include initials when necessary: J.S. Bach")
    nationality = models.CharField("Nationality", max_length=30)
    birth = models.PositiveSmallIntegerField("Year of birth")
    death = models.PositiveSmallIntegerField("Year of death", blank=True,
                                             null=True)

    class Meta:
        ordering = 'short_name',

    def __str__(self):
        if self.death:
            return "{name} ({birth}–{death})".format(**self.__dict__)
        return "{name} (b. {birth})".format(**self.__dict__)

    panels = (
        FieldPanel('name', classname='full title'),
        FieldPanel('short_name', classname='full'),
        MultiFieldPanel([
            FieldPanel('nationality', classname='full'),
            FieldPanel('birth'),
            FieldPanel('death'),
        ], "Details"),
    )


@register_snippet
class Piece(models.Model):
    title = models.CharField(max_length=255)
    composer = models.ForeignKey('music.Composer')

    def __str__(self):
        return "{title}, {composer}".format(title=self.title, composer=self.composer.short_name)

    panels = (
        FieldPanel('title', classname='full title'),
        SnippetChooserPanel('composer'),
    )
